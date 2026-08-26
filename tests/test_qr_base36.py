from utils.base36 import decode_base36, encode_base36


#value = '174UZPT' 

value = input("ENter the value from qr code")

decoded_value =decode_base36(value)
print('decoded - ',decoded_value)

encoded_value = encode_base36(int(decoded_value))

print('encoded - ',encoded_value)




