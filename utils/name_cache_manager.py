from models.models import Initials, Session

class NameCacheManager:
    def __init__(self):
        self.first_name_cache = []
        self.last_name_cache = []
        self.legendary_name_cache = []
        
    async def load_caches(self):
        session = Session()
        
        try:
            for name in session.query(Initials).filter_by(type=0).all():
                self.first_name_cache.append(name.value)
            for name in session.query(Initials).filter_by(type=1).all():
                self.last_name_cache.append(name.value)
            for name in session.query(Initials).filter_by(type=2).all():
                self.legendary_name_cache.append(name.value)
        except:
            print('error while loading name caches.')
        finally:
            session.close()
            
    async def add_name(self, name: str, type: int):
        """
        name: string
        type: 0 - first name, 1 - last name, 2 - legendary name
        """
        session = Session()
        try:
            # add name if it is not exists consider lowercase and uppercase      
            if type == 0:
                name = name.strip()
                if name.lower() in [x.lower() for x in self.first_name_cache]: return
                self.first_name_cache.append(name)
            elif type == 1:
                if name.lower() in [x.lower() for x in self.last_name_cache]: return
                self.last_name_cache.append(name)
            elif type == 2:
                if name.lower() in [x.lower() for x in self.legendary_name_cache]: return
                self.legendary_name_cache.append(name)
            new_name = Initials(value=name, type=type)
            session.add(new_name)
            session.commit()
            print(f"Имя {name} типа {'first name' if type == 0 else 'last name' if type == 1 else 'legendary name'} добавлено в кэш и базу данных.")
        except:
            print('error while adding name to cache and database.')
        finally:
            session.close()
            
    def delete_initial(self, value, type):
        if type not in (0,1,2): return
        session = Session()
        try:
            if type == 0:
                for name in self.first_name_cache:
                    if name.lower() == value.lower():
                        self.first_name_cache.remove(name)
                        session.query(Initials).filter_by(value=name, type=0).delete()
            elif type == 1:
                for name in self.last_name_cache:
                    if name.lower() == value.lower():
                        self.last_name_cache.remove(name)
                        session.query(Initials).filter_by(value=name, type=1).delete()
            elif type == 2:
                for name in self.legendary_name_cache:
                    if name.lower() == value.lower():
                        self.legendary_name_cache.remove(name)
                        session.query(Initials).filter_by(value=name, type=2).delete()
            session.commit()
        except:
            print('error while deleting initials from cache and database.')
        finally:
            session.close()