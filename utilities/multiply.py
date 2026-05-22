def multiply(*args):
    """
    Multiply two or more values, coerce to numbers if possible, and round to 2 decimal places.
    
    Args:
        *args: Variable number of arguments to multiply
    
    Returns:
        float: Product rounded to 2 decimal places, or 0 if no valid numbers
    """
    numbers = []
    
    for arg in args:
        try:
            # Try to convert to float (handles ints, floats, and numeric strings)
            num = float(arg)
            numbers.append(num)
        except (TypeError, ValueError):
            # Skip values that can't be converted to numbers
            continue
    
    if not numbers:
        return 0.0
    
    product = 1
    for num in numbers:
        product *= num
    
    # Round to 2 decimal places
    return round(product, 2)


if __name__ == "__main__":
    print(multiply(2, 3))
    print(multiply(2, 3, 4))
    print(multiply(5, 10, 2, 3))
    print(multiply(7))
    print(multiply(2.5, 3.7))
    print(multiply(2, "3", 4))
    print(multiply("1.5", "2.5", 3))
    print(multiply(2.555, 3))
    print(multiply("abc", 5, "2"))
    print(multiply())
