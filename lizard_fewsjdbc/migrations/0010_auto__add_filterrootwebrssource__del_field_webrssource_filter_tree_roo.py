# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FilterRootWebRSSource'
        db.create_table('lizard_fewsjdbc_filterrootwebrssource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('webrs_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_fewsjdbc.WebRSSource'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('filter_tree_root', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_fewsjdbc', ['FilterRootWebRSSource'])

        # Deleting field 'WebRSSource.filter_tree_root'
        db.delete_column('lizard_fewsjdbc_webrssource', 'filter_tree_root')

        # Deleting field 'WebRSSource.slug'
        db.delete_column('lizard_fewsjdbc_webrssource', 'slug')

        # Adding field 'WebRSSource.source_code'
        db.add_column('lizard_fewsjdbc_webrssource', 'source_code',
                      self.gf('django.db.models.fields.CharField')(default=datetime.datetime(2013, 9, 2, 0, 0), max_length=50),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'FilterRootWebRSSource'
        db.delete_table('lizard_fewsjdbc_filterrootwebrssource')

        # Adding field 'WebRSSource.filter_tree_root'
        db.add_column('lizard_fewsjdbc_webrssource', 'filter_tree_root',
                      self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True),
                      keep_default=False)

        # Adding field 'WebRSSource.slug'
        db.add_column('lizard_fewsjdbc_webrssource', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default=datetime.datetime(2013, 9, 2, 0, 0), max_length=50),
                      keep_default=False)

        # Deleting field 'WebRSSource.source_code'
        db.delete_column('lizard_fewsjdbc_webrssource', 'source_code')


    models = {
        'lizard_fewsjdbc.filtercache': {
            'Meta': {'object_name': 'FilterCache'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'filterid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'is_end_node': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sub_filter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_fewsjdbc.filterrootwebrssource': {
            'Meta': {'object_name': 'FilterRootWebRSSource'},
            'filter_tree_root': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']"})
        },
        'lizard_fewsjdbc.iconstyle': {
            'Meta': {'object_name': 'IconStyle'},
            'color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'fews_filter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_parameter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.JdbcSource']", 'null': 'True', 'blank': 'True'}),
            'mask': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'lizard_fewsjdbc.iconstylewebrs': {
            'Meta': {'object_name': 'IconStyleWebRS'},
            'color': ('lizard_map.fields.ColorField', [], {'max_length': '8'}),
            'fews_filter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'fews_parameter': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'}),
            'mask': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'lizard_fewsjdbc.jdbcsource': {
            'Meta': {'object_name': 'JdbcSource'},
            'connector_string': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'customfilter': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filter_tree_root': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jdbc_tag_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'jdbc_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'timezone_string': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'usecustomfilter': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'lizard_fewsjdbc.locationcache': {
            'Meta': {'object_name': 'LocationCache'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'locationid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parent_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tooltiptext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_fewsjdbc.parametercache': {
            'Meta': {'object_name': 'ParameterCache'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameter_group': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameter_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'parameterid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_fewsjdbc.threshold': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Threshold'},
            'color': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '6'}),
            'filter_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parameter_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '8'})
        },
        'lizard_fewsjdbc.timeseriescache': {
            'Meta': {'object_name': 'TimeseriesCache'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            't_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.FilterCache']"}),
            't_location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.LocationCache']"}),
            't_parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.ParameterCache']"}),
            'webrs_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_fewsjdbc.WebRSSource']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_fewsjdbc.webrssource': {
            'Meta': {'object_name': 'WebRSSource'},
            'base_path': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'source_code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['lizard_fewsjdbc']