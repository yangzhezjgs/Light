import pymysql
class BaseDB:
     def __init__(self, user, password, database='', host='127.0.0.1', port=3306, charset='utf8', cursor_class=pymysql.cursors.DictCursor):
        self.user = user                    # 连接用户
        self.password = password            # 连接用户密码
        self.database = database            # 选择的数据库
        self.host = host                    # 主机名，默认 127.0.0.1
        self.port = port                    # 端口号，默认 3306
        self.charset = charset              # 数据库编码，默认 UTF-8
        self.cursor_class = cursor_class    # 数据库游标类型，默认为 DictCursor，返回的每一行数据集都是个字典
        self.conn = self.connect()        # 数据库连接对
     def connect(self):
        return pymysql.connect(host=self.host, user=self.user, port=self.port,passwd=self.password, db=self.database,charset=self.charset,cursorclass=self.cursor_class)

     def execute(self, sql, params=None):
        with self.conn as cursor:
            rows = cursor.execute(sql, params) if params and isinstance(params, dict) else cursor.execute(sql)
            result = cursor.fetchall()
        return rows, result

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)
class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        # skip base Model class:
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        if not '__database__' in attrs:
            attrs['__database__'] = 'default'
        attrs['db'] = BaseDB('root','123456',database = attrs['__database__'])
        return type.__new__(cls, name, bases, attrs)

class Model(dict,metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("'%s' instance has no attribute '%s'" % (self.__class__.__name__, key))

    def __setattr__(self, key, value):
        self[key]=value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value
    @classmethod
    def filter(cls,where='', *args):
        sql='select * from %s %s' % (cls.__table__,'where %s'%where if where else '')
        print(sql)
        L,res=cls.db.execute(sql)
        print(res)
        return res
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        print(self.__insert__,args)
        sql = self.__insert__.replace("?", "'%s'")%(args[0],args[1],args[2])
        print(sql)
        rows,res = self.db.execute(sql)
        return res
