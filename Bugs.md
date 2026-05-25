# Bug Report: FastAPI User Orders Endpoint

## Bug 1: Password is exposed in the API response

### Issue

The endpoint returns the user's password in every order response:

```python
"password": user.password
```

This is a serious security vulnerability. Passwords should never be exposed through an API response, even if they are hashed.

### Fix

Remove the password from the response.

```python
result.append({
    "id": order.id,
    "total": order.total_amount
})
```

---

## Bug 2: Missing check for non-existent user

### Issue

The code fetches the user like this:

```python
user = db.query(User).filter(User.id == user_id).first()
```

If no user exists with that `user_id`, then `user` will be `None`.

Later, the code tries to access:

```python
user.password
```

This will cause an error:

```text
AttributeError: 'NoneType' object has no attribute 'password'
```

### Fix

Check whether the user exists before continuing.

```python
from fastapi import HTTPException

if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

---

## Bug 3: Inefficient database query

### Issue

The code retrieves all orders from the database:

```python
orders = db.query(Order).all()
```

Then it filters them manually in Python:

```python
if order.user_id == user_id:
```

This is inefficient because the application loads every order, even orders that do not belong to the requested user.

### Fix

Filter the orders directly in the database query.

```python
orders = db.query(Order).filter(Order.user_id == user_id).all()
```

---

# Corrected Code

```python
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

@app.get("/users/{user_id}/orders")
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    orders = db.query(Order).filter(Order.user_id == user_id).all()

    result = []

    for order in orders:
        result.append({
            "id": order.id,
            "total": order.total_amount
        })

    return result
```

---

# Summary

| Number | Bug | Fix |
|---|---|---|
| 1 | Password is exposed in the API response | Remove `password` from the returned data |
| 2 | User may not exist | Add a `404` check if `user` is `None` |
| 3 | All orders are loaded and filtered in Python | Filter orders directly in the database query |
