class EnvironmentSettings:
    def __init__(self):
        self.workspace_dir = '/media/cs303-2/DATA/hza/hcat/'    # Base directory for saving network checkpoints.
        self.tensorboard_dir = self.workspace_dir + '/tensorboard/'    # Directory for tensorboard files.
        self.lasot_dir = ''
        self.got10k_dir = '/media/cs303-2/DATA/hza/data/got10k/test_data/test/'
        self.trackingnet_dir = ''
        self.coco_dir = '/media/cs303-2/DATA/hza/data/coco2017/'
        self.lvis_dir = ''
        self.sbd_dir = ''
        self.birdsai_dir = '/media/cs303-2/DATA/hza/data/BirdSAI/'



        self.imagenet_dir = ''
        self.imagenetdet_dir = ''
        self.ecssd_dir = ''
        self.hkuis_dir = ''
        self.msra10k_dir = ''
        self.davis_dir = ''
        self.youtubevos_dir = ''
