_window_title = "RsWdolA"
_caesar_shift = 3

def caesar_cipher(text, shift):
    encrypted_text = ""
    for char in text:
        # 文字がアルファベットの場合のみ処理を行う
        if char.isalpha():
            # 大文字と小文字で処理を分ける
            if char.isupper():
                # 大文字の場合はアルファベットの範囲を超えないようにシフトする
                encrypted_text += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                # 小文字の場合も同様にシフトする
                encrypted_text += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
        else:
            # アルファベット以外の文字はそのまま追加する
            encrypted_text += char
    return encrypted_text


def window_title():
    return caesar_cipher(_window_title, _caesar_shift * -1)
