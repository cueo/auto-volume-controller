import applescript

val = 20
# applescript.AppleScript('set volume output volume ' + str(val)).run()
x = applescript.AppleScript('get volume settings').run()
print x[applescript.AEType('ouvl')]
