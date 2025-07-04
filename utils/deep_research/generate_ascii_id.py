import hashlib

def generate_ascii_id(text: str) -> str:
    """
    テキストからASCII文字のみのIDを生成する関数
    PineconeはベクトルIDにASCII文字のみを要求するため、
    日本語を含むテキストをハッシュ化して一意のIDを生成します。
    Args:
        text (str): 元のテキスト（日本語可）
    Returns:
        str: ASCII文字のみのID（例: vec_a1b2c3d4...）
    """
    hash_object = hashlib.md5(text.encode('utf-8'))
    return f"vec_{hash_object.hexdigest()}"
