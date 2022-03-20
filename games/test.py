def State_to_Str(board_state):
    result = ""
    for i in range(3):
        for j in range(3):
            result+=str(2 if board_state[i][j]==-1 else  board_state[i][j])
    return result
def Str_to_State(board_string):
    s = board_string
    result = ((2 if int(s[0]) == 2 else int(s[0]),2 if int(s[1]) == 2 else int(s[1]),2 if int(s[2]) == 2 else int(s[2])),
                (2 if int(s[3]) == 2 else int(s[3]),2 if int(s[4]) == 2 else int(s[4]),2 if int(s[5]) == 2 else int(s[5])),
                (2 if int(s[6]) == 2 else int(s[6]),2 if int(s[7]) == 2 else int(s[7]),2 if int(s[8]) == 2 else int(s[8])))
    return result
def simpleAI(net,side):
    #0 means null;1 means X;2 means O;
    str1 = State_to_Str(net)
    for i in range(9):
        if(side == -1):
            if(str1[i] == '2'):
                str1[i] == '1'
            if(str1[i] == '1'):
                str1[i] == '2'
    net = Str_to_State(str1)
    level = [[0,0,0],[0,0,0],[0,0,0]]
    o2=10000#一个己方活二权值
    x2=1000#一个对方活二权值
    x=10#一个对方活一权值
    o=6#一个己方活一权值
    nothing = 4#一个空行权值

    for i in range(3):
        for j in range(3):
            if(net[i][j]!=0):
                 level[i][j]=0
            else:
                 #自己活二,,220
                if(((net[0][j]+net[1][j]+net[2][j])==4) and (net[0][j]*net[1][j]*net[2][j])==0 and ((net[0][j]-1)*(net[1][j]-1)*(net[2][j]-1))==-1):
                    level[i][j]=level[i][j]+o2
                if(((net[i][0]+net[i][1]+net[i][2])==4) and (net[i][0]*net[i][1]*net[i][2])==0 and ((net[i][0]-1)*(net[i][1]-1)*(net[i][2]-1))==-1):
                    level[i][j]=level[i][j]+o2
                #对方活二，110
                if(((net[0][j]+net[1][j]+net[2][j])==2) and (net[0][j]*net[1][j]*net[2][j])==0 and ((net[0][j]-1)*(net[1][j]-1)*(net[2][j]-1))==0):
                    level[i][j]=level[i][j]+x2
                if(((net[i][0]+net[i][1]+net[i][2])==2) and (net[i][0]*net[i][1]*net[i][2])==0 and ((net[i][0]-1)*(net[i][1]-1)*(net[i][2]-1))==0):
                    level[i][j]=level[i][j]+x2
                #单个X，100
                if(((net[0][j]+net[1][j]+net[2][j])==1) and (net[0][j]*net[1][j]*net[2][j])==0 and ((net[0][j]-1)*(net[1][j]-1)*(net[2][j]-1))==0):
                    level[i][j]=level[i][j]+x
                if(((net[i][0]+net[i][1]+net[i][2])==1)and(net[i][0]*net[i][1]*net[i][2])==0 and ((net[i][0]-1)*(net[i][1]-1)*(net[i][2]-1))==0):
                    level[i][j]=level[i][j]+x
                #单个O，200
                if(((net[0][j]+net[1][j]+net[2][j])==2)and(net[0][j]*net[1][j]*net[2][j])==0 and((net[0][j]-1)*(net[1][j]-1)*(net[2][j]-1))==1):
                    level[i][j]=level[i][j]+o
                if(((net[i][0]+net[i][1]+net[i][2])==2)and(net[i][0]*net[i][1]*net[i][2])==0 and((net[i][0]-1)*(net[i][1]-1)*(net[i][2]-1))==1):
                    level[i][j]=level[i][j]+o
                #空行，000
                if(((net[0][j]+net[1][j]+net[2][j])==0)and(net[0][j]*net[1][j]*net[2][j])==0 and((net[0][j]-1)*(net[1][j]-1)*(net[2][j]-1))==-1):
                    level[i][j]=level[i][j]+nothing
                if(((net[i][0]+net[i][1]+net[i][2])==0)and(net[i][0]*net[i][1]*net[i][2])==0 and ((net[i][0]-1)*(net[i][1]-1)*(net[i][2]-1))==-1):
                    level[i][j]=level[i][j]+nothing
            
                #分情况 主对角线
                if((i==0 and j==0)or(i==2 and j==2)or(i==1 and j==1)):
                    #己方活二
                    if(((net[0][0]+net[1][1]+net[2][2])==4)and(net[0][0]*net[1][1]*net[2][2])==0 and((net[0][0]-1)*(net[1][1]-1)*(net[2][2]-1))==-1):
                        level[i][j]=level[i][j]+o2
                    #对方活二
                    if(((net[0][0]+net[1][1]+net[2][2])==2)and(net[0][0]*net[1][1]*net[2][2])==0 and((net[0][0]-1)*(net[1][1]-1)*(net[2][2]-1))==0):
                        level[i][j]=level[i][j]+x2
                    #单个X
                    if(((net[0][0]+net[1][1]+net[2][2])==1)and(net[0][0]*net[1][1]*net[2][2])==0 and((net[0][0]-1)*(net[1][1]-1)*(net[2][2]-1))==0):
                        level[i][j]=level[i][j]+x
                    #单个O
                    if(((net[0][0]+net[1][1]+net[2][2])==2) and(net[0][0]*net[1][1]*net[2][2])==0 and((net[0][0]-1)*(net[1][1]-1)*(net[2][2]-1))==1):
                        level[i][j]=level[i][j]+o
                    #空行，000
                    if(((net[0][0]+net[1][1]+net[2][2])==0) and(net[0][0]*net[1][1]*net[2][2])==0 and((net[0][0]-1)*(net[1][1]-1)*(net[2][2]-1))==-1):
                        level[i][j]=level[i][j]+nothing
            
                #副对角线
                if((i==0 and j==2)or(i==2 and j==0)or(i==1 and j==1)):
                    #己方活二
                    if(((net[0][2]+net[1][1]+net[2][0])==4) and(net[0][2]*net[1][1]*net[2][0])==0 and((net[0][2]-1)*(net[1][1]-1)*(net[2][0]-1))==-1):
                        level[i][j]=level[i][j]+o2
                    #对方活二
                    if(((net[0][2]+net[1][1]+net[2][0])==2) and(net[0][2]*net[1][1]*net[2][0])==0 and((net[0][2]-1)*(net[1][1]-1)*(net[2][0]-1))==0):
                        level[i][j]=level[i][j]+x2
                    #单个X
                    if(((net[0][2]+net[1][1]+net[2][0])==1) and(net[0][2]*net[1][1]*net[2][0])==0 and((net[0][2]-1)*(net[1][1]-1)*(net[2][0]-1))==0):
                        level[i][j]=level[i][j]+x
                    #单个O
                    if(((net[0][2]+net[1][1]+net[2][0])==2) and(net[0][2]*net[1][1]*net[2][0])==0 and((net[0][2]-1)*(net[1][1]-1)*(net[2][0]-1))==1):
                        level[i][j]=level[i][j]+o
                    #空行，000
                    if(((net[0][2]+net[1][1]+net[2][0])==0) and(net[0][2]*net[1][1]*net[2][0])==0 and((net[0][2]-1)*(net[1][1]-1)*(net[2][0]-1))==-1):
                        level[i][j]=level[i][j]+nothing



    #寻找最大权值的位置
    maxi = 0
    maxj = 0
    temp = 0
    for i in range(3):
        for j in range(3):
            if(level[i][j]>temp):
                temp=level[i][j]
                maxi=i
                maxj=j
    move = (maxi,maxj)

    return move
