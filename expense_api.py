from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Программа учета расходов API", version="1.0")

# модель данных
class Expense(BaseModel):
    id: Optional[int] = None
    amount: float
    category: str
    description: str = ""
    date: str = datetime.now().strftime("%Y-%m-%d")

# типа БД)
expenses_db: List[dict] = []
next_id = 1


@app.get("/health") # проверка доступности API
def health_check():
    return {"status": "ok"}

@app.get("/expenses") # получить список всех расходов
def get_expenses():
    return {"expenses": expenses_db, "total": len(expenses_db)}

@app.post("/expenses", status_code=201) # добавить новый расход
def create_expense(expense: Expense):
    global next_id
    expense_data = expense.model_dump()
    expense_data["id"] = next_id
    next_id += 1
    expenses_db.append(expense_data)
    return expense_data

@app.get("/expenses/{expense_id}") # получить расход по ID
def get_expense(expense_id: int):
    for exp in expenses_db:
        if exp["id"] == expense_id:
            return exp
    raise HTTPException(status_code=404, detail="Расход не найден")

@app.put("/expenses/{expense_id}") # обновить расход
def update_expense(expense_id: int, expense: Expense):
    for i, exp in enumerate(expenses_db):
        if exp["id"] == expense_id:
            updated = expense.model_dump()
            updated["id"] = expense_id
            expenses_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Расход не найден")

@app.delete("/expenses/{expense_id}") # удалить расход
def delete_expense(expense_id: int):
    for i, exp in enumerate(expenses_db):
        if exp["id"] == expense_id:
            deleted = expenses_db.pop(i)
            return {"message": f"Расход '{deleted['description']}' удалён"}
    raise HTTPException(status_code=404, detail="Расход не найден")

@app.get("/expenses/category/{category}") # получить расходы по категории
def get_expenses_by_category(category: str):
    filtered = [exp for exp in expenses_db if exp["category"].lower() == category.lower()]
    return {"category": category, "expenses": filtered, "count": len(filtered)}