from utils.cleaners import clean_symbol, clean_stock_name


def test_clean_symbol():
    assert clean_symbol("123") == ""
    assert clean_symbol("ab c") == "ABC"
    assert clean_symbol("abC123D") == "ABCD"
    assert clean_symbol(" 1&$%^# T#S__#L#A#") == "TSLA"
    assert clean_symbol("ABC^D") == "ABCD"


def test_clean_stock_name():
    assert clean_stock_name("Apple") == "Apple"
    assert clean_stock_name("Apple Inc.") == "Apple Inc"
    assert clean_stock_name("Common Stocks Company Common Share 10%") == "Common Stocks Company"
    assert clean_stock_name("Some Awesome Corporation +10 dividends / year") == "Some Awesome Corp"
    assert clean_stock_name("Some Awesome Company with too much info") == "Some Awesome Company"
    assert clean_stock_name("Another Awesome Business Limited Stock A Common Shares") == "Another Awesome Business Limited"
