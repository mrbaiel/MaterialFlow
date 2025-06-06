from aiogram.fsm.state import State, StatesGroup


class AddBatchState(StatesGroup):
    product = State()
    quantity = State()
    date = State()


class AddSubBatchState(StatesGroup):
    batch = State()
    quantity = State()
    employees = State()


class AddEmployeeState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    address = State()


class AddClientState(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    address = State()


class AddOrderState(StatesGroup):
    client = State()
    date = State()
    initial_payment = State()


class AddOrderItemState(StatesGroup):
    order = State()
    product = State()
    quantity = State()
