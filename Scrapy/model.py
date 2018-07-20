from pony import orm as manejador

manejador.sql_debug(True)
db = manejador.Database()
db2 = manejador.Database()

db.bind('postgres', user="postgres", password='#1105@jp', host='localhost', database='sbcdata')
db2.bind('postgres', user="postgres", password='#1105@jp', host='localhost', database='sbc')

class Data(db.Entity):
    id = manejador.PrimaryKey(int, auto=True)
    sujeto = manejador.Required(str)
    predicado = manejador.Required(str)
    objeto = manejador.Required(str)
db.generate_mapping(check_tables=True, create_tables=True)

class Info(db2.Entity):
    id = manejador.PrimaryKey(int, auto=True)
    sujeto = manejador.Required(str)
    predicado = manejador.Required(str)
    objeto = manejador.Required(str)
    reconciliation = manejador.Optional(str)

db2.generate_mapping(check_tables=True, create_tables=True)
