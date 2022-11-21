# Generated by Django 3.2.15 on 2022-11-08 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0046_auto_20221108_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='block',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='classes_taught',
            field=models.CharField(blank=True, choices=[('primary', 'Primary'), ('middle', 'Middle'), ('secondary', 'Secondary'), ('senior_secondary', 'Senior Secondary'), ('other', 'Other')], db_index=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='company',
            field=models.CharField(blank=True, choices=[('aif', 'AIF'), ('pratham', 'Pratham'), ('bharti', 'Bharti Foundation'), ('other', 'Other')], db_index=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='distribution_model',
            field=models.CharField(blank=True, choices=[('indi', 'Independent'), ('integrated', 'Integrated'), ('other', 'Other')], db_index=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='district',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='referer',
            field=models.CharField(blank=True, choices=[('rf', 'Refferal'), ('org', 'Organisation'), ('ad', 'Advertisment'), ('other', 'Other')], db_index=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='tag_label',
            field=models.TextField(blank=True, null=True, verbose_name='Tag Label'),
        ),
    ]
