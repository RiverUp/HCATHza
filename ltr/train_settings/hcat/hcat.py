# -*-coding:utf-8-*-
import torch
from ltr.dataset import Lasot, MSCOCOSeq, Got10k, TrackingNet, BirdSAI
from ltr.data import processing, sampler, LTRLoader
import ltr.models.tracking.hcat as hcat_models
from ltr import actors
from ltr.trainers import LTRTrainer
import ltr.data.transforms as tfm
from ltr import MultiGPU
from ltr.trainers.hcat_trainer import HCATLTRTrainer
import os
# os.environ["CUDA_VISIBLE_DEVICES"]= "0, 1"

def run(settings):
    # Most common settings are assigned in the settings struct
    settings.device = 'cuda'
    settings.description = 'TransT with default settings.'
    settings.batch_size = 128
    settings.num_workers = 4
    settings.multi_gpu = False
    settings.print_interval = 1
    settings.normalize_mean = [0.485, 0.456, 0.406]
    settings.normalize_std = [0.229, 0.224, 0.225]
    settings.search_area_factor = 4.0
    settings.template_area_factor = 2.0
    settings.search_feature_sz = 32
    settings.template_feature_sz = 16
    settings.search_sz = settings.search_feature_sz * 8
    settings.temp_sz = settings.template_feature_sz * 8
    settings.center_jitter_factor = {'search': 3, 'template': 0}
    settings.scale_jitter_factor = {'search': 0.25, 'template': 0}

    settings.backbone = 'resnet18'

    # Transformer
    settings.position_embedding = 'sine'
    settings.hidden_dim = 256
    settings.dropout = 0.1
    settings.nheads = 8
    settings.dim_feedforward = 2048
    settings.featurefusion_layers = 2

    torch.backends.cudnn.enabled = False
    print(torch.backends.cudnn.enabled)

    # Train datasets

    # lasot_train = Lasot(settings.env.lasot_dir, split='train')
    # got10k_train = Got10k(settings.env.got10k_dir, split='all')
    # got10k_train = Got10k(settings.env.got10k_dir, split='vottrain')
    # trackingnet_train = TrackingNet(settings.env.trackingnet_dir, set_ids=list(range(12)))
    # coco_train = MSCOCOSeq(settings.env.coco_dir)
    birdsai_train = BirdSAI(settings.env.birdsai_dir)

    # The joint augmentation transform, that is applied to the pairs jointly
    transform_joint = tfm.Transform(tfm.ToGrayscale(probability=0.05))

    # The augmentation transform applied to the training set (individually to each image in the pair)
    transform_train = tfm.Transform(tfm.ToTensorAndJitter(0.2),
                                    tfm.Normalize(mean=settings.normalize_mean, std=settings.normalize_std))

    # Data processing to do on the training pairs
    data_processing_train = processing.TransTProcessing(search_area_factor=settings.search_area_factor,
                                                      template_area_factor = settings.template_area_factor,
                                                      search_sz=settings.search_sz,
                                                      temp_sz=settings.temp_sz,
                                                      center_jitter_factor=settings.center_jitter_factor,
                                                      scale_jitter_factor=settings.scale_jitter_factor,
                                                      mode='sequence',
                                                      transform=transform_train,
                                                      joint_transform=transform_joint)

    # The sampler for training
    dataset_train = sampler.HCATSampler([birdsai_train], [1],
                                          samples_per_epoch=1000 * settings.batch_size, max_gap=100,
                                          processing=data_processing_train)
    # dataset_train = sampler.HCATSampler([lasot_train, got10k_train, coco_train, trackingnet_train], [1,1,1,1],
    #                             samples_per_epoch=50000, max_gap=100, processing=data_processing_train)

    # dataset_train = sampler.HCATSampler([lasot_train], [1],
    #                             samples_per_epoch=1000*settings.batch_size, max_gap=100, processing=data_processing_train)

    # The loader for training
    loader_train = LTRLoader('train', dataset_train, training=True, batch_size=settings.batch_size, num_workers=settings.num_workers,
                             shuffle=True, drop_last=True, stack_dim=0)

    # Create network and actor
    model = hcat_models.hcat(settings)

    # Wrap the network for multi GPU training
    if settings.multi_gpu:
        model = MultiGPU(model, dim=0)

    objective = hcat_models.hcat_loss(settings)
    n_parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print('number of params:', n_parameters)

    actor = actors.HCATActor(net=model, objective=objective)

    # Optimizer
    param_dicts = [
        {"params": [p for n, p in model.named_parameters() if "backbone" not in n and p.requires_grad]},
        {
            "params": [p for n, p in model.named_parameters() if "backbone" in n and p.requires_grad],
            "lr": 1e-5,
        },
    ]
    optimizer = torch.optim.AdamW(param_dicts, lr=1e-4,
                                  weight_decay=1e-4)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 150)

    # Create trainer
    trainer = LTRTrainer(actor, [loader_train], optimizer, settings, lr_scheduler)

    # Run training (set fail_safe=False if you are debugging)
    trainer.train(200, load_latest=True, fail_safe=True)
