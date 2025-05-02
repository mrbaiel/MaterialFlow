class BillingPortalView(APIView):
    """STRIPE ENDPOINT: /billing_portal"""

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            payment_integration = (
                get_payment_integration_service().get_payment_integration(
                    user_id=request.user.id,
                    payment_type=constants.STRIPE,
                )
            )

            if not payment_integration.metadata.get("customer_id"):
                logger.error(f"Company missing stripe_id: {request.user.id}")
                return Response(
                    {"error": "Stripe setup incomplete for this company"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return_url = f"{settings.FRONTEND_HOST}general"
            billing_url = stripe_manager.create_billing_portal_session(
                payment_integration.metadata["customer_id"], return_url
            )

            return Response({"url": billing_url}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in billing portal view: {str(e)}")
            return Response(
                {"error": "Failed to create billing portal session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeConnectView(APIView):
    """STRIPE ENDPOINT: /stripe/connect"""


    def get(self, request, *args, **kwargs):
        try:
            existing_app = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )
            api_key = existing_app.metadata.get("api_key")
            return Response(
                {
                    "hasStripe": bool(existing_app),
                    "api_key": api_key,
                }
            )
        except Exception as e:
            print(f"Error checking Stripe connection: {str(e)}")
            return Response({"error": "Failed to check Stripe connection"}, status=500)


    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            api_key = request.data.get("api_key")

            if not api_key:
                return Response(
                    {"success": False, "error": "API key is required"}, status=400
                )

            # existing_app = db.apps.find_one(
            #     {
            #         "user_id": ObjectId(user_id),
            #         "type": "stripe",
            #     }
            # )
            existing_app = get_payment_integration_service().get_payment_integration(
                user_id=user_id, payment_type=constants.STRIPE
            )

            if existing_app:
                return Response(
                    {"success": False, "error": "Stripe account already connected"},
                    status=400,
                )


            get_payment_integration_service().update_payment_integration(
                user_id=user_id,
                payment_type=constants.STRIPE,
                metadata={
                    "api_key": api_key,
                },
            )

            # db.apps.insert_one(new_app)
            return Response({"success": True})

        except Exception as e:
            print(f"Error saving Stripe connection: {str(e)}")
            return Response({"success": False, "error": str(e)}, status=500)

    def delete(self, request):
        try:
            get_payment_integration_service().delete_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )

            return Response({"success": True})

        except Exception as e:
            print(f"Error disconnecting Stripe: {str(e)}")
            return Response(
                {"success": False, "error": "Failed to disconnect Stripe"}, status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeCredentialsAPIView(APIView):
    """STRIPE ENDPOINT: /stripe/credentials"""

    def get(self, request):
        try:
            # stripe_data = db.apps.find_one({"user_id": user_id, "type": "stripe"})
            stripe_data = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )

            if not stripe_data:
                return Response(
                    {"success": False, "error": "Stripe not connected"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            api_key = stripe_data.metadata["api_key"]
            return Response({"success": True, "api_key": api_key})

        except Exception as e:
            print(f"Error getting Stripe credentials: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeSubscriptionAPIView(APIView):
    """STRIPE ENDPOINT: /stripe/subscription"""

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            print(f"Checking subscription for user_id: {user_id}")

            # stripe_data = db.apps.find_one({"user_id": user_id, "type": "stripe"})
            stripe_data = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )
            if not stripe_data:
                return Response(
                    {"success": False, "error": "Stripe not connected"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            stripe.api_key = stripe_data.metadata["api_key"]
            subscription = stripe.Subscription.retrieve(
                stripe_data.metadata["subscription_id"]
            )

            formatted_subscription = {
                "id": subscription["id"],
                "status": subscription["status"],
                "current_period_start": subscription["current_period_start"],
                "current_period_end": subscription["current_period_end"],
                "plan": {
                    "name": subscription["plan"].get("nickname", "Standard Plan"),
                    "amount": subscription["plan"].get("amount", 0) / 100,
                    "currency": subscription["plan"].get("currency", "USD"),
                    "interval": subscription["plan"].get("interval", "month"),
                },
            }

            print("Formatted subscription data:", formatted_subscription)
            return Response({"success": True, "subscription": formatted_subscription})

        except stripe.error.StripeError as e:
            print(f"Stripe API error: {str(e)}")
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(f"General error: {str(e)}")
            traceback.print_exc()
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeChargesAPIView(APIView):
    """STRIPE ENDPOINT: /stripe/charges"""


    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            print(f"Checking charges for user_id: {user_id}")

            # stripe_data = db.apps.find_one({"user_id": user_id, "type": "stripe"})
            stripe_data = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )

            if not stripe_data:
                return Response(
                    {"success": False, "error": "Stripe not connected"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            stripe.api_key = stripe_data.metadata["api_key"]
            charges = stripe.Charge.list(limit=10)

            formatted_charges = {
                "charges": [
                    {
                        "id": charge["id"],
                        "amount": charge["amount"] / 100,
                        "currency": charge["currency"].upper(),
                        "status": charge["status"],
                        "date": datetime.fromtimestamp(charge["created"]).strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "description": charge.get("description", "No description"),
                        "paid": charge["paid"],
                    }
                    for charge in charges["data"]
                ]
            }

            print("Formatted charges data:", formatted_charges)
            return Response({"success": True, "charges": formatted_charges})

        except stripe.error.StripeError as e:
            print(f"Stripe API error: {str(e)}")
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(f"General error: {str(e)}")
            traceback.print_exc()
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeInvoicesAPIView(APIView):
    """STRIPE ENDPOINT: /stripe/invoices"""

    def get(self, request):
        try:
            user_id = request.user.id
            print(f"Checking invoices for user_id: {user_id}")

            stripe_data = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )
            # stripe_data = db.apps.find_one({"user_id": user_id, "type": "stripe"})

            if not stripe_data:
                return Response(
                    {"success": False, "error": "Stripe not connected"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            stripe.api_key = stripe_data.metadata["api_key"]
            invoices = stripe.Invoice.list(limit=10)

            formatted_invoices = [
                {
                    "id": invoice["id"],
                    "number": invoice.get("number", "N/A"),
                    "amount_due": invoice["amount_due"] / 100,
                    "currency": invoice["currency"].upper(),
                    "status": invoice["status"],
                    "date": datetime.fromtimestamp(invoice["created"]).strftime(
                        "%Y-%m-%d"
                    ),
                    "due_date": (
                        datetime.fromtimestamp(invoice["due_date"]).strftime("%Y-%m-%d")
                        if invoice.get("due_date")
                        else "N/A"
                    ),
                    "paid": invoice["paid"],
                    "period_start": (
                        datetime.fromtimestamp(invoice["period_start"]).strftime(
                            "%Y-%m-%d"
                        )
                        if invoice.get("period_start")
                        else "N/A"
                    ),
                    "period_end": (
                        datetime.fromtimestamp(invoice["period_end"]).strftime(
                            "%Y-%m-%d"
                        )
                        if invoice.get("period_end")
                        else "N/A"
                    ),
                }
                for invoice in invoices["data"]
            ]

            print("Formatted invoices data:", formatted_invoices)
            return Response({"success": True, "invoices": formatted_invoices})

        except stripe.error.StripeError as e:
            print(f"Stripe API error: {str(e)}")
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(f"General error: {str(e)}")
            traceback.print_exc()
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeSubscriptionPauseAPIView(APIView):
    """STRIPE ENDPOINT: /stripe/pause-subscription"""

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            print(f"Pausing subscription for user_id: {user_id}")

            # stripe_data = db.apps.find_one({"user_id": user_id, "type": "stripe"})
            stripe_data = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )
            if not stripe_data:
                return Response(
                    {"success": False, "error": "Stripe not connected"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            stripe.api_key = stripe_data.metadata["api_key"]
            subscription = stripe.Subscription.modify(
                stripe_data.metadata["subscription_id"],
                pause_collection={"behavior": "mark_uncollectible"},
            )


            return Response(
                {
                    "success": True,
                    "subscription": {
                        "status": subscription["status"],
                        "current_period_end": subscription["current_period_end"],
                    },
                }
            )

        except Exception as e:
            print(f"Error pausing subscription: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeSubscriptionCancelAPIView(APIView):
    """STRIPE ENDPOINT: /stripe/cancel-subscription"""


    def post(self, request):
        try:
            user_id = request.user.id
            data = request.data
            cancel_at_period_end = data.get("cancel_at_period_end", True)
            print(f"Canceling subscription for user_id: {user_id}")

            stripe_data = get_payment_integration_service().get_payment_integration(
                user_id=request.user.id, payment_type=constants.STRIPE
            )
            if not stripe_data:
                return Response(
                    {"success": False, "error": "Stripe not connected"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            stripe.api_key = stripe_data.metadata["api_key"]
            if cancel_at_period_end:
                print("📤 Requesting end-of-period cancellation...")
                subscription = stripe.Subscription.modify(
                    stripe_data.metadata["subscription_id"], cancel_at_period_end=True
                )
            else:
                print("📤 Requesting immediate cancellation...")
                subscription = stripe.Subscription.delete(
                    stripe_data.metadata["subscription_id"]
                )

            return Response(
                {
                    "success": True,
                    "subscription": {
                        "status": subscription["status"],
                        "cancel_at_period_end": subscription["cancel_at_period_end"],
                        "current_period_end": subscription["current_period_end"],
                    },
                }
            )

        except Exception as e:
            print(f"Error canceling subscription: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
