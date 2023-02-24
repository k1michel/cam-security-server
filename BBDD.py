import dataset

class Basededatos:
    fichero_sqlite: str = 'base_datos.db' 
    videos = None

    def __init__(self):

        self.db = dataset.connect(
            f'sqlite:///{Basededatos.fichero_sqlite}?check_same_thread=False')  # sirve para que varios procesos simultaneos se puedan ejecutar sin que salte warning
        # creamos instancia q mediante dataset la conectamos con nuestro fichero de la base de datos
        self.videos = self.db['videos']

    def insertar_video(self,file):
        return self.videos.insert(file)

    def mostrar_video(self):
        return [dict(videos) for videos in self.videos.all()]
    
    def eliminar_video(self):
        self.videos.delete()
        return
