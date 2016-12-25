import subprocess

#cmd = 'echo $(vcgencmd measure_temp)'
#cmd = ['vcgencmd measure_temp']

p = subprocess.Popen(['vcgencmd', 'measure_temp'])
out, err = p.communicate()

print(out)
