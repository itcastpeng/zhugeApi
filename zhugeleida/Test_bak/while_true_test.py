

global Flag
def Test():
    Flag = ''
    while True:
        print('---->>1 while')
        while Flag:
            print('------2 while')

        Flag = True

        return 'ok'

Test()