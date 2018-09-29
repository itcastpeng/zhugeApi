

seconds = 0
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)



if not h and not m and s:
    print("%s秒" % (s))
elif  not h  and  m and s:
    print ("%s分%s秒" % (m, s))

elif  h and m and s:
    print ("%s时%s分%s秒" % (h, m, s))