def sum(*args):
    """
    Sum two or more values, coerce to numbers if possible.
    
    Args:
        *args: Variable number of arguments to sum
    
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
    
    sum = 0
    for num in numbers:
        sum += num
    
    # Round to 2 decimal places
    return sum


if __name__ == "__main__":
    print(sum(2, 3))
    print(sum(2, 3, 4))
    print(sum(5, 10, 2, 3))
    print(sum(7))
    print(sum(2.5, 3.7))
    print(sum(2, "3", 4))
    print(sum("1.5", "2.5", 3))
    print(sum(2.555, 3))
    print(sum("abc", 5, "2"))
    print(sum())
