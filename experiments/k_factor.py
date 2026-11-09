import matplotlib.pyplot as plt

test_k_max = 50
test_k_min = 15
test_taget_voices = 50


def k_function(voices, k_min, k_max, target_voices, remaining_fraction):

    s = target_voices / (1 / remaining_fraction - 1)
    k_factor = (k_min * voices + k_max * s) / (s + voices)

    return k_factor


x = []
y = []

for i in range(100):
    x.append(i)
    y.append(k_function(i, test_k_min, test_k_max, test_taget_voices))

for j in y:
    if j <= test_k_max - 0.9 * (test_k_max - test_k_min):
        print(y.index(j))
        break

plt.plot(x, y)
print(x)
print(y)
plt.show()
