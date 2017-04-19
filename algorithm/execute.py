# coding=utf-8
import pymysql


def getConnection():
    conn = pymysql.connect(host='localhost', db='supervision', user='root', passwd='root', port=3306,
                           charset='utf8')  # 之后可以放到配置文件中读取
    return conn


def createtable(target, field):
    conn = getConnection()
    cur = conn.cursor()
    curstr = "DROP TABLE IF EXISTS `"
    curstr += target
    curstr += "`;"
    curstr += "CREATE TABLE "
    curstr += target
    curstr += "(`id` int(11) NOT NULL AUTO_INCREMENT ,"
    for i in range(len(field)):
        curstr += "`%s`" % (field[i])
        curstr += " int(11) NOT NULL,"
    curstr += "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(curstr)

    curstr = "DROP TABLE IF EXISTS `"
    curstr += target
    curstr += "_codes"
    curstr += "`;"
    curstr += "CREATE TABLE "
    curstr += target
    curstr += "_codes"
    curstr += " (`id` int(11) NOT NULL AUTO_INCREMENT,`name` varchar(45) NOT NULL,`column` int(11) NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(curstr)

    # curstr="DROP TABLE IF EXISTS `"
    # curstr+=target
    # curstr+="_apriorirules"
    # curstr+="`;"
    # curstr+="CREATE TABLE "
    # curstr+=target
    # curstr+="_apriorirules (`id` int(11) NOT NULL AUTO_INCREMENT,"
    # for i in range(0,len(field)):
    #     curstr+="`front_"
    #     curstr+=field[i]
    #     curstr+="` int(11) DEFAULT NULL,"
    # for i in range(0,len(field)):
    #     curstr+="`back_"
    #     curstr+=field[i]
    #     curstr+="` int(11) DEFAULT NULL,"
    # curstr+=" `support` double NOT NULL,`confidence` double NOT NULL,`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    # cur.execute(curstr)

    curstr = "DROP TABLE IF EXISTS `"
    curstr += target
    curstr += "_middle"
    curstr += "`;"
    curstr += "CREATE TABLE "
    curstr += target
    curstr += "_middle (`id` int(11) NOT NULL AUTO_INCREMENT,"
    for i in range(0, len(field)):
        curstr += "`%s`" % (field[i])
        curstr += " varchar(45) DEFAULT NULL,"
    curstr += " `support` double NOT NULL,`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,`alert` int(11) NOT NULL DEFAULT 0, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(curstr)

    curstr = "DROP TABLE IF EXISTS `"
    curstr += target
    curstr += "_except"
    curstr += "`;"
    curstr += "CREATE TABLE "
    curstr += target
    curstr += "_except "
    curstr += "(`id` int(11) NOT NULL,"
    curstr += "PRIMARY KEY (`id`)"
    curstr += ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(curstr)
    # curstr="DROP TABLE IF EXISTS `"
    # curstr+=target
    # curstr+="_result"
    # curstr+="`;"
    # curstr+="CREATE TABLE "
    # curstr+=target
    # curstr+="_result (`id` int(11) NOT NULL AUTO_INCREMENT,"
    # for i in range(0,len(field)):
    #     curstr+="`%s`"%(field[i])
    #     curstr+=" varchar(45) DEFAULT NULL,"
    # curstr+=" `support` double NOT NULL,`type` int(11) NOT NULL,`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    # cur.execute(curstr)


    curstr = "DROP VIEW IF EXISTS `"
    curstr += target
    curstr += "_count"
    curstr += "`;"
    curstr += "CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW "
    curstr += target
    curstr += "_count AS "
    for i in range(len(field)):
        curstr += "SELECT "
        curstr += "`%s`" % (target)
        curstr += " . "
        curstr += "`%s`" % (field[i])
        curstr += " AS `pid`, COUNT(0) AS `sum`,"
        curstr += "`%s" % (target)
        curstr += "_codes` . "
        curstr += "`column` FROM ("
        curstr += "`%s" % (target)
        curstr += "_codes` JOIN "
        curstr += "`%s`" % (target)
        curstr += " ) WHERE ( "
        curstr += "`%s" % (target)
        curstr += "_codes`.`id` = "
        curstr += "`%s`" % (target)
        curstr += " . "
        curstr += "`%s`)" % (field[i])
        curstr += " GROUP BY "
        curstr += "`%s`" % (target)
        curstr += " . "
        curstr += "`%s`" % (field[i])
        if i < len(field) - 1:
            curstr += " UNION "
    cur.execute(curstr)

    curstr = "DROP TABLE IF EXISTS `"
    curstr += target
    curstr += "_generules"
    curstr += "`;"
    curstr += "CREATE TABLE "
    curstr += target
    curstr += "_generules "
    curstr += "(`id` int(11) NOT NULL AUTO_INCREMENT ,"
    for i in range(len(field)):
        curstr += "`%s`" % (field[i])
        # curstr+=" int(11),"
        curstr += " varchar(45) ,"
    curstr += "`fit` double NOT NULL,`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,`alert` int(11) NOT NULL DEFAULT 0,"
    curstr += "PRIMARY KEY (`id`),"
    curstr += "UNIQUE KEY `uk_t_1` ("
    for i in range(len(field)):
        curstr += "`%s`," % (field[i])
    curstr = curstr[:-1]
    curstr += (")")
    curstr += ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(curstr)

    cur.close()
    conn.commit()
    conn.close()


def preexecute(target, field):
    conn = pymysql.connect(host='localhost', user='root', passwd='root', port=3306, charset='utf8')
    cur = conn.cursor()
    cur.execute("USE supervision")
    curstr = "INSERT INTO "
    curstr += target + "_codes"
    curstr += "( `name`,`column`) VALUES ( '%s','%d')" % (unicode("凌晨", "utf-8"), 0)
    cur.execute(curstr)
    curstr = "INSERT INTO "
    curstr += target + "_codes"
    curstr += "( `name`,`column`) VALUES ( '%s','%d')" % (unicode("上午", "utf-8"), 0)
    cur.execute(curstr)
    curstr = "INSERT INTO "
    curstr += target + "_codes"
    curstr += "( `name`,`column`) VALUES ( '%s','%d')" % (unicode("下午", "utf-8"), 0)
    cur.execute(curstr)
    curstr = "INSERT INTO "
    curstr += target + "_codes"
    curstr += "( `name`,`column`) VALUES ( '%s','%d')" % (unicode("晚上", "utf-8"), 0)
    cur.execute(curstr)
    curstr = "SELECT * FROM "
    curstr += target + "_raw"
    cur.execute(curstr)
    res = cur.fetchall()
    for row in res:
        data = []
        time = row[1].strftime("%H")  # 默认row[1]为时间
        if (int)(time) < 6:
            data += [1]
        elif (int)(time) < 12:
            data += [2]
        elif (int)(time) < 18:
            data += [3]
        else:
            data += [4]
        for i in range(2, len(field) + 1):
            selc = "SELECT id FROM "
            selc += target + "_codes"
            selc += " where `name`='%s'and `column`='%d'" % (row[i], i - 1)
            cur.execute(selc)
            res2 = cur.fetchall()
            if len(res2) == 0:
                curstr = "INSERT INTO "
                curstr += target + "_codes"
                curstr += "( `name`,`column`)VALUES ( '%s','%d')" % (row[i], i - 1)
                cur.execute(curstr)
                cur.execute(selc)
                res2 = cur.fetchall()
                data += [res2[0][0]]
            else:
                data += [res2[0][0]]
        print data
        curstr = "INSERT INTO "
        curstr += target
        curstr += "("
        for i in range(len(field)):
            curstr += "`" + field[i] + "`,"
        curstr = curstr[:-1]
        curstr += ") VALUES("
        for i in range(len(data)):
            curstr += str(data[i]) + ","
        curstr = curstr[:-1]
        curstr += ")"
        cur.execute(curstr)
    cur.close()
    conn.commit()
    conn.close()


def data_process_ippacket_preexecute():
    field = ["time", "host_id", "send_mac_address", "recv_mac_address", "send_ip", "send_port", "recv_ip", "recv_port"]
    target = "data_process_ippacket"
    createtable(target, field)
    preexecute(target, field)


def warning_information_preexecute():
    field = ["time", "userid", "description", "rank", "species"]
    target = "warning_information"
    createtable(target, field)
    preexecute(target, field)


def data_process_fileinfo_file_preexecute():
    field = ["time", "file_name", "user", "operate_type", "host_id"]
    target = "data_process_fileinfo_file"
    createtable(target, field)
    preexecute(target, field)


def data_process_fileinfo_type_preexecute():
    field = ["time", "file_type", "user", "operate_type", "host_id"]
    target = "data_process_fileinfo_type"
    createtable(target, field)
    preexecute(target, field)


def data_process_resource_warning_preexecute():
    field = ["time", "user", "process_name", "resource_name", "warning_rank"]
    target = "data_process_resource_warning"
    createtable(target, field)
    preexecute(target, field)
