# coding=gbk
"""
genefunc.py
~~~~~~~~~~~~~~~~
ʹ���Ŵ��㷨�ھ�����
���룺ref ��Ϊģʽ��
codes: ��Ϊ����ź�Ȩ�أ�Ŀǰ������ΪȨ�ض���ͬ���ɸĳɸ���Ϊ���ֵ�Ƶ��
�����
�û���������Ϊģʽ����
���ܵ���ʾ�����û���������Ϊģʽ���������mysql���ݿ�ʱ����Ϊ�ظ����ݲ��뱨����(���ǲ���Ӱ�������)
"""
import random
import copy

import pymysql

NS = 1#���п��ܵ���Ϊ��Ŀ��Ŀǰ����Ϊ42������readcodes�л�ȡ
ST = 1#��Ϊģʽ��Ĵ�С,��readref�л��
LEN = 4#��Ϊģʽ���еĳ���,��readref�л��
CNUM = 8#Ⱥ���ģ
NUM = 15#��������

#����
class Chrom:
    def __init__(self):
        self.seq = [0] * LEN#��Ϊģʽ����
        self.M = 0
        self.fit = 0.0#��Ӧ��

    def Ccopy(self, a):
        self.seq = copy.copy(a.seq)
        self.M = a.M
        self.fit = a.fit

    def show(self):
        print self.seq
        print self.M
        print self.fit


class Code:
    def __init__(self, _id, _count,_column):
        self.id = _id
        self.count = _count
        self.column=_column
#��ʼ��Ⱥ��

def getConnection():
    conn = pymysql.connect(host='localhost',db='supervision', user='root', passwd='root', port=3306, charset='utf8')#֮����Էŵ������ļ��ж�ȡ
    return conn
def evpop(codes, ref):
    pop = []
    i = 0
    codes_column={}
    for c in codes:
        codes_column.setdefault(c.column,[])
        codes_column[c.column]+=[c.id]
    while (i < CNUM):
        chrom = Chrom()
        j = 0
        while (j < LEN):
            chrom.seq[j] = codes_column[j][random.randint(0, len(codes_column[j]) - 1)]
            j += 1
        # if random.randint(0,1)>0:
        #     chrom.seq[random.randint(0,LEN-1)]=0#���ֹ���
        calculatefit(chrom, codes, ref)
        pop += [chrom]
        i += 1
    return pop

#�������
def crossover(popcurrent, codes):
    popnext = []
    i = 0
    while i < CNUM - 1:
        j = i + 1
        while j < CNUM:
            if 80 > random.randint(1, 100):
                c1 = Chrom()
                c2 = Chrom()
                crosspoint = random.randint(0, LEN - 1)
                k = 0
                while k < crosspoint:
                    c1.seq[k] = popcurrent[i].seq[k]
                    c2.seq[k] = popcurrent[j].seq[k]
                    k += 1
                while k < LEN:
                    c1.seq[k] = popcurrent[j].seq[k]
                    c2.seq[k] = popcurrent[i].seq[k]
                    k += 1
                popnext += [c1]
                popnext += [c2]
            j += 1
        i += 1
    return popnext

#�������
def mutation(popnext, codes, ref):
    for chrom in popnext:
        i = 0
        while i < LEN:
            if random.randint(0, 99) < 5:
                chrom.seq[i] = random.randint(1, NS)
            i += 1
        calculatefit(chrom, codes, ref)

#��Ȼѡ�����
def pickchroms(popcurrent, popnext):
    ret = popcurrent + popnext
    ret.sort(key=lambda obj: obj.fit, reverse=True)
    ret = ret[:CNUM]
    return ret

#������Ӧ�Ⱥ���
def calculatefit(chrom, codes, ref):
    # E = LEN
    ci = 0.0
    i = 0
    while i < LEN:
        if chrom.seq[i] != 0:
            ci += codes[chrom.seq[i] - 1].count
        # else:
        #     E -= 1
        i += 1
    j = 0
    while j < ST:
        eq = True
        k = 0
        while k < LEN:
            pop = chrom.seq[k]
            if 0 != pop and ref[j][k] != pop:
                eq = False
                break
            k += 1
        if eq:
            chrom.M += 1
        j += 1
    # chrom.fit = ci * chrom.M * pow(NS, E) / ST
    chrom.fit = ci * chrom.M

#��ȡref ���LEN��ST
def readref(target):
    ref = []
    try:
        conn =getConnection()
        cur = conn.cursor()
        sql="SELECT * FROM "
        sql+=target
        cur.execute(sql)
        res = cur.fetchall()
        global ST
        ST= len(res)
        global LEN
        LEN=len(res[0])-1
        for row in res:
            temp = [0] * LEN
            for index in range(len(row) - 1):
                temp[index] = row[index + 1]
            ref += [temp]
        cur.close()
        conn.commit()
        conn.close()
        return ref
    except  Exception:
        print("error")

#��ȡcount ���NS
def readcounts(target):
    codes = []
    conn = getConnection()
    cur = conn.cursor()
    sql="SELECT * FROM "
    sql+=target
    sql+=" order by pid"
    cur.execute(sql)
    res = cur.fetchall()
    for row in res:
        id=row[0]
        percent=(float)(row[1])/ST
        a = Code(id,percent,row[2])
        codes += [a]
    global NS
    NS=len(codes)
    cur.close()
    conn.commit()
    conn.close()
    return codes
#�鿴pop���Ƿ�������Ⱥ�Ѿ�ȫ����ͬ��ȫ����ͬ��ֹͣ����
def checkequal(pop):
    c=pop[0].seq
    eq=True
    for chrom in pop:
        if chrom.seq !=c:
            eq=False
            break
    return eq

#���������Ϊģʽ�����ݿ�
def writerules(popcurrent,target,codes,field):
    conn = getConnection()
    cur = conn.cursor()
    basesql2 = "SELECT * FROM "
    basesql2+= codes
    basesql2+= " where id="
    basesql="INSERT IGNORE INTO "+target+"("
    for i in range(len(field)):
        basesql+="`"+field[i]+"`,"
    basesql+="`fit`) VALUES("
    for chrom in popcurrent:
        sql=basesql
        for i in range(len(field)):
            csql=basesql2
            csql+=str(chrom.seq[i])
            cur.execute(csql)
            res=cur.fetchall()
            sql+="'%s',"%(res[0][1])
        sql+='%lf)'%(chrom.fit)
        cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
def getrules(target,field):
    ref = readref(target)
    codes = readcounts(target+"_count")
    popcurrent = evpop(codes, ref)
    dd = 0
    while dd < NUM:
        print "��ǰΪ��%d�ֵ���" % (dd)
        if checkequal(popcurrent):
            break
        popnext = crossover(popcurrent, codes)
        mutation(popnext, codes, ref)
        popnext = pickchroms(popcurrent, popnext)
        popcurrent = popnext
        dd += 1
    writerules(popcurrent,target+"_generules",target+"_codes",field)
def get_ip_packet_rules():
    field=["time","host_id","send_mac_address","recv_mac_address","send_ip","send_port","recv_ip","recv_port"]
    getrules("data_process_ippacket",field)
def get_warning_information_rules():
    field=["time","userid","description","rank","species"]
    getrules("warning_information",field)
def get_data_process_fileinfo_file_rules():
    field=["time","file_name","user","operate_type","host_id"]
    getrules("data_process_fileinfo_file",field)
def get_data_process_fileinfo_type_rules():
    field=["time","file_type","user","operate_type","host_id"]
    getrules("data_process_fileinfo_type",field)
def get_data_process_resource_warning_rules():
    field = ["time", "user", "process_name", "resource_name", "warning_rank"]
    getrules("data_process_resource_warning", field)

#��ѯ��Ϊģʽ����Ӧ��ֵ��֮�������ֵ�����ж��Ƿ�����
def search_fit(target,seq):
    chrom=Chrom()
    chrom.seq=seq
    ref=readref(target)
    codes=readcounts(target+"_count")
    calculatefit(chrom,codes,ref)
    return chrom.fit

