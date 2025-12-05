from fastapi import FastAPI

app = FastAPI(title="Calculator", version="0.1")


@app.get("/calculation/sum")
def calc(a: int, b: int):
    sum_ = a + b
    return sum_


@app.get("/calculation/mult")
def multi(a: int, b: int):
    multip = a * b
    return multip
