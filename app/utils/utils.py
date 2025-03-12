def convert_id_to_chat_id(dict: dict) -> dict:
    """
    Convert the _id to chat_id in a dictionary.
    """
    dict['chat_id'] = dict.pop('_id')
    return dict