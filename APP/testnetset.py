



# HOST_PORT_LAYER_0_81 = HOST_PORT_LAYER_0_origin + 2*129# 番目の後続ドメイン
# HOST_PORT_LAYER_1_81 = HOST_PORT_LAYER_0_81 + 1
s = 251
v = 251

print(hex(s))

for i in range(10):
    X = "HOST_PORT_LAYER_0_" + str(hex(s+i)[2:]) + " = HOST_PORT_LAYER_0_origin + 2*" + str(v+i)
    Y = "HOST_PORT_LAYER_1_" + str(hex(s+i)[2:]) + " = HOST_PORT_LAYER_0_" + str(hex(s+i)[2:]) + " + 1"
    print(X)
    print(Y)


"""
x = 400
y = 2
for i in range(200):
    if i % 2 == 0:
        print("50" + str(x+i) + " : 1" )
"""
