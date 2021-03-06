
from south.db import db
from django.db import models
from photogallery.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
        db.alter_column('photogallery_photo', 'slug', models.SlugField(_('slug'), 
            blank=False, null=False, unique=True, max_length=255))
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
        db.alter_column('photogallery_photo', 'slug', models.SlugField(_('slug'), 
            blank=True, null=True, unique=False, max_length=255))
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photogallery.photo': {
            'album': ('models.ForeignKey', ['Album'], {'related_name': "'photos'", 'null': 'True', 'verbose_name': "_('album')", 'blank': 'True'}),
            'created_at': ('models.DateTimeField', [], {'auto_now_add': 'True', 'verbose_name': "_('created at')"}),
            'description': ('models.TextField', [], {'null': 'True', 'verbose_name': "_('description')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', [], {'verbose_name': "_('image path')", 'max_length': '255'}),
            'is_featured': ('models.BooleanField', [], {'default': 'False', 'verbose_name': "_('is featured')"}),
            'is_published': ('models.BooleanField', [], {'default': 'False', 'verbose_name': "_('is published')"}),
            'shoot_date': ('models.DateField', [], {'null': 'True', 'verbose_name': "_('shot date')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('slug')"], {'unique': 'True', 'max_length': 255}),
            'title': ('models.CharField', [], {'verbose_name': "_('title')", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now_add': 'True', 'auto_now': 'True', 'verbose_name': "_('updated at')"}),
            'uploader': ('models.ForeignKey', ['User'], {'related_name': "'uploaded_photos'", 'null': 'True', 'verbose_name': "_('uploader')", 'blank': 'True'})
        },
        'photogallery.album': {
            'created_at': ('models.DateTimeField', [], {'auto_now_add': 'True', 'verbose_name': "_('created at')"}),
            'default_image': ('models.ImageField', [], {'db_column': "'image'", 'max_length': '255', 'blank': 'True', 'null': 'True', 'verbose_name': "_('default photo')"}),
            'description': ('models.TextField', [], {'null': 'True', 'verbose_name': "_('description')", 'blank': 'True'}),
            'display_order': ('models.PositiveIntegerField', [], {'default': '0', 'verbose_name': "_('display order')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('models.BooleanField', [], {'default': 'False', 'verbose_name': "_('is published')"}),
            'slug': ('models.SlugField', [], {'max_length': '255', 'unique': 'True'}),
            'title': ('models.CharField', [], {'max_length': '255', 'verbose_name': "_('title')"}),
            'updated_at': ('models.DateTimeField', [], {'auto_now_add': 'True', 'auto_now': 'True', 'verbose_name': "_('updated at')"})
        }
    }
    
    complete_apps = ['photogallery']
