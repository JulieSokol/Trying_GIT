import numpy as np

T19V = np.array([[213.9,220.2,220.1],
                 [203.1,209.5,211.5],
                 [192.4,198.7,202.8]])
T19H = np.array([[160.5,171.2,170.1],
                [142.4,152.2,155.4],
                [124.2,133.2,140.6]])
T37V = np.array([[227.5,232.1,233.1],
                [221.2,225.6,227.3],
                [214.9,219.1,221.4]])
T37H = np.array([[184.5,193.2,193.6],
                [172.6,180.5,182.4],
                [160.6,167.8,171.2]])
T85V = np.array([[244.4,249.5,252.3],
                [242.2,246.5,249.4],
                [244.2,245.7,245.3]])
T85H = np.array([[213.8,228.5,236.9],
                [204.9, 215.1,226.0],
                [208.4,213.5,215.6]])

# Add dimentions
def add_dim (arr2d):
  return np.expand_dims(arr2d, axis=2)
# Calculate tg: tg(85-37 H)
def tan85_37h(p85h, p37h):
  return (p85h - p37h) / (85.5 - 37)

# Calculate tg: tg(85-19 V)
def tan85_19v(p85v, p19v):
  return (p85v - p19v) / (85.5 - 19.35)

# Calculate tg: tg(37-19 V)
def tan37_19v(p37v, p19v):
  return (p37v - p19v) / (37 - 19.35)

# Set linear function for F1 (85H and 37H)
def f85_37h(I):
  return -0.085 * I + 0.908

# Set linear function for F1 (85V and 19V)
def f85_19v(I):
  return -0.86 * I + 0.55

# Set linear function for F2 (85H and 37H)
def phi85_37h(I):
  return -0.039 * I + 1.19

# Set linear function for F2 (85V and 19V)
def phi85_19v(I):
  return -0.04 * I + 0.7

# Make a range of concentrations from 0% to 100% (in tenths)
I = np.arange(0, 10.1, 0.1)

# Set function #1
def F1(I, T85H, T37H, T85V, T19V):
  return 0.5 * ((f85_37h(I) - tan85_37h(T85H, T37H)) ** 2 / tan85_37h(T85H, T37H) ** 2 +
                (f85_19v(I) - tan85_19v(T85V, T19V)) ** 2 / tan85_19v(T85V, T19V) ** 2)

def F2(I, T85H, T37H, T85V, T19V):
  return 0.5 * ((phi85_37h(I) - tan85_37h(T85H, T37H)) ** 2 / tan85_37h(T85H, T37H) ** 2 +
                (phi85_19v(I) - tan85_19v(T85V, T19V)) ** 2 / tan85_19v(T85V, T19V) ** 2)

# Set linear function for checking puddles
def delta37_19v(I_min):
  return -0.187 * I_min + 1.1


def I1_to_I2(i1, i2, tg37_19v):
  if delta37_19v(i1) < tg37_19v:
    return i1
  else:
    return i2


vectI1_to_I2 = np.vectorize(I1_to_I2)

T19V = add_dim(T19V)
T19H = add_dim(T19H)
T37V = add_dim(T37V)
T37H = add_dim(T37H)
T85V = add_dim(T85V)
T85H = add_dim(T85H)

I1_min = np.argmin(F1(I, T85H, T37H, T85V, T19V), axis=2) / 10
I2_min = np.argmin(F2(I, T85H, T37H, T85V, T19V), axis=2) / 10



result = vectI1_to_I2(I1_min, I2_min, tan37_19v(T37V, T19V)[:, :, 0])

print("True concentration", result)
print("Pudlles", I2_min - I1_min)