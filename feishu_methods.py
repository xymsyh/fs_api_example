def find_column_letter(header_data, target_id_text):
    """
    Find the column letter for a given target in the header row.
    Supports more than 26 columns (A, B, ..., Z, AA, AB, ...)

    :param header_data: List of headers.
    :param target_id_text: The target header substring to find.
    :return: Column letter as a string or an error message if not found.
    """
    if not header_data or not header_data[0]:
        return "Header is empty or invalid"

    def column_to_letter(column_index):
        """
        Convert a zero-indexed column number to a column letter (A, B, ..., AA, AB, ...)
        
        :param column_index: Zero-indexed column number.
        :return: Corresponding column letter.
        """
        column_letter = ''
        while column_index >= 0:
            column_letter = chr(column_index % 26 + 65) + column_letter
            column_index = column_index // 26 - 1
        return column_letter

    for i, column_name in enumerate(header_data[0]):
        if target_id_text in column_name:
            return column_to_letter(i)

    return "Target not found in header"
