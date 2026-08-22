import pytest
from app.services.extraction import (
    extract_text_from_txt,
    extract_text_from_pdf,
    extract_text,
    convert_table_to_text,
    is_valid_cell
)


# ----------------------------------------
# is_valid_cell tests
# ----------------------------------------

def test_valid_cell_normal():
    """normal text should be valid"""
    assert is_valid_cell("Hemoglobin") == True


def test_valid_cell_none():
    """None should be invalid"""
    assert is_valid_cell(None) == False


def test_valid_cell_empty_string():
    """empty string should be invalid"""
    assert is_valid_cell("") == False


def test_valid_cell_dash():
    """dash should be invalid (empty marker)"""
    assert is_valid_cell("-") == False


def test_valid_cell_na():
    """n/a should be invalid (empty marker)"""
    assert is_valid_cell("n/a") == False


def test_valid_cell_colon():
    """colon should be invalid (empty marker)"""
    assert is_valid_cell(":") == False


def test_valid_cell_number():
    """number should be valid"""
    assert is_valid_cell("12.5") == True


# ----------------------------------------
# extract_text_from_txt tests
# ----------------------------------------

def test_extract_txt_basic():
    """basic txt extraction should work"""
    content = b"Hello this is test content"
    text = extract_text_from_txt(content)
    assert "Hello" in text
    assert len(text) > 0


def test_extract_txt_empty():
    """empty bytes should return empty string"""
    content = b""
    text = extract_text_from_txt(content)
    assert text == ""


def test_extract_txt_multiline():
    """multiline text should be extracted correctly"""
    content = b"line one\nline two\nline three"
    text = extract_text_from_txt(content)
    assert "line one" in text
    assert "line two" in text
    assert "line three" in text


def test_extract_txt_special_characters():
    """special characters should be handled"""
    content = "Hello! Price: $100.00".encode("utf-8")
    text = extract_text_from_txt(content)
    assert "Hello" in text
    assert "$100.00" in text


def test_extract_txt_unicode():
    """unicode characters should be handled"""
    content = "Mijanur Rahman".encode("utf-8")
    text = extract_text_from_txt(content)
    assert "Mijanur" in text


# ----------------------------------------
# convert_table_to_text tests
# ----------------------------------------

def test_convert_table_basic():
    """basic table should convert to text"""
    table = [
        ["Test", "Value", "Normal Range"],
        ["Hemoglobin", "12.5", "13-17"],
        ["WBC", "7500", "4000-11000"]
    ]
    result = convert_table_to_text(table, page_num=1)
    assert "Hemoglobin" in result
    assert "12.5" in result
    assert "WBC" in result


def test_convert_table_empty():
    """empty table should return empty string"""
    result = convert_table_to_text([], page_num=1)
    assert result == ""


def test_convert_table_single_row():
    """table with only header row should return empty"""
    table = [["Test", "Value"]]
    result = convert_table_to_text(table, page_num=1)
    assert result == ""


def test_convert_table_invalid_headers():
    """table with all invalid headers should return empty"""
    table = [
        ["-", "n/a", "--"],
        ["data1", "data2", "data3"]
    ]
    result = convert_table_to_text(table, page_num=1)
    assert result == ""


def test_convert_table_mixed_valid_invalid_cells():
    """table with some invalid cells should skip them"""
    table = [
        ["Name", "Value", "Unit"],
        ["Hemoglobin", "-", "g/dL"],    # Value is invalid (dash)
        ["WBC", "7500", "n/a"]          # Unit is invalid (n/a)
    ]
    result = convert_table_to_text(table, page_num=1)
    assert "Hemoglobin" in result
    assert "WBC" in result
    assert "7500" in result


# ----------------------------------------
# extract_text (main entry point) tests
# ----------------------------------------

def test_extract_text_txt_type():
    """extract_text should handle txt file type"""
    content = b"test content here"
    text = extract_text(content, "txt")
    assert "test content" in text


def test_extract_text_invalid_type():
    """invalid file type should raise ValueError"""
    content = b"some content"
    with pytest.raises(ValueError) as exc_info:
        extract_text(content, "docx")
    assert "Unsupported file type" in str(exc_info.value)


def test_extract_text_empty_content():
    """empty content should raise ValueError"""
    content = b""
    with pytest.raises(ValueError) as exc_info:
        extract_text(content, "txt")
    assert "No text could be extracted" in str(exc_info.value)


def test_extract_text_whitespace_only():
    """whitespace only content should raise ValueError"""
    content = b"   \n\n\t  "
    with pytest.raises(ValueError) as exc_info:
        extract_text(content, "txt")
    assert "No text could be extracted" in str(exc_info.value)
