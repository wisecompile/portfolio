---- initialize
function OnInit()
    host = "ProductionSQL"                -- name of the ODBC connector
    login = "masterOPC"                   -- login username
    password = "******"                   -- login password

    env = odbc.env_create()              -- create ODBC environment object
    CONN, s = odbc.env_connect(env, host, login, password)  -- attempt connection

    if (CONN == nil) then
        server.Message(s)                -- print error message if connection fails
    end
end

---- deinitialize
function OnClose()
    odbc.conn_close(CONN)                -- close connection
    odbc.env_close(env)                  -- close environment
    odbc.cur_close(res)                  -- close cursor (if open)
end

---- handling
function OnBeforeReading()

    -- Step 1: fetch the latest serial number from a buffer table
    cur0, s = odbc.conn_execute(CONN, [[
        SELECT serialNum
        FROM dbo.tokenCNC
    ]])
    if cur0 == nil then
        server.Message("Error - ", s)
        odbc.conn_close(CONN)
        return
    end
    row0 = odbc.cur_fetch(cur0)
    serialNum = row0.serialNum

    -- Step 2: retrieve SKU and moldNum for this serial number
    local SQL_1 = [[
        SELECT SKU, moldNum
        FROM serialSKU
        WHERE serialNum =
    ]]
    SQL_1 = SQL_1 .. string.format("('%s')", serialNum)
    cur1, s = odbc.conn_execute(CONN, SQL_1)
    if cur1 == nil then
        server.Message("Error - ", s)
        odbc.conn_close(CONN)
        return
    end
    row1 = odbc.cur_fetch(cur1)
    SKU = row1.SKU
    moldNum = row1.moldNum

    -- Step 3: retrieve Z-axis correction (a1z) based on moldNum
    local SQL_2 = [[
        SELECT a1z
        FROM moldNum
        WHERE moldNum =
    ]]
    SQL_2 = SQL_2 .. string.format("('%s')", moldNum)
    cur2, s = odbc.conn_execute(CONN, SQL_2)
    if cur2 == nil then
        server.Message("Error - ", s)
        odbc.conn_close(CONN)
        return
    end
    row2 = odbc.cur_fetch(cur2)
    a1z = row2.a1z
end

---- handling
function OnAfterReading()

    -- Write values to Modbus OPC tags
    server.WriteTag("Modbus TCP .ID_2.Model", string.sub(SKU, 1, 2))
    server.WriteTagToDevice("Modbus TCP .ID_2.Model", string.sub(SKU, 1, 2))

    server.WriteTag("Modbus TCP .ID_2.Mold", moldNum)
    server.WriteTagToDevice("Modbus TCP .ID_2.Mold", moldNum)

    server.WriteTag("Modbus TCP .ID_2.a1z_SQL", a1z)
    server.WriteTagToDevice("Modbus TCP .ID_2.a1z_SQL", a1z)

    -- Check if spindle correction was entered manually on HMI
    res, s = server.ReadTag("Modbus TCP .ID_2.a1z_token")
    if res ~= 0000 then
        -- Write manual correction value back to SQL
        local SQL_3 = [[
            UPDATE moldNum
            SET a1z =
        ]]
        SQL_3 = SQL_3 .. string.format("('%s') WHERE moldNum = ('%s')", res, moldNum)
        res1, s = odbc.conn_execute(CONN, SQL_3)
        if res1 == nil then
            server.Message("Error - ", s)
            odbc.conn_close(CONN)
            return
        end
        -- Reset the manual correction tag
        server.WriteTag("Modbus TCP .ID_2.a1z_token", 0000)
        server.WriteTagToDevice("Modbus TCP .ID_2.a1z_token", 0000)
    end

    -- Close all cursors
    odbc.cur_close(cur0)
    odbc.cur_close(cur1)
    odbc.cur_close(cur2)
end
