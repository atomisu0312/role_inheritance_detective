import re

def process_upper_template(input_str, variables):
    """
    "${upper("${var.env}_...")}" のような形式の文字列を処理する
    """
    
    # 1. 外側の ${upper(...)} から中身（引数）を抽出
    #    正規表現: r'\$\{upper\((.+)\)\}'
    #    (.+) が引数部分にマッチします
    outer_match = re.search(r'\$\{upper\((.+)\)\}', input_str)
    
    if not outer_match:
        return "Error: ${upper(...)} pattern not found."
        
    # 2. 中身（引数）を取得します
    #    例: \"${var.env}_MART_TLC_MABLS_MOTION_BOARD\"
    content = outer_match.group(1)
    
    # 3. 中身が引用符（"）で囲まれていたら削除します
    #    例: ${var.env}_MART_TLC_MABLS_MOTION_BOARD
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1] # 最初と最後の " を削除
        
    # 4. 中身の文字列（content）に対して、内側の変数置換（${...}）を実行
    def replace_var(match):
        key = match.group(1) # マッチしたキー（例: "var.env"）
        # variables 辞書から値を取得。見つからなければ元の文字列（例: "${var.env}"）を返す
        return variables.get(key, match.group(0))

    # re.sub を使って、${...} 形式の変数すべてを置換します
    # 例: dev_MART_TLC_MABLS_MOTION_BOARD
    processed_content = re.sub(r'\$\{([^}]+)\}', replace_var, content)
    
    # 5. 最後に upper() の処理（大文字化）を実行
    final_result = processed_content.upper()
    
    return final_result