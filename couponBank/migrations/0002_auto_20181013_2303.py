# Generated by Django 2.0.5 on 2018-10-13 23:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('couponBank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('success', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='products',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='couponBank.Product'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='orders',
            field=models.ManyToManyField(to='couponBank.Order'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='couponBank.UserProfile'),
        ),
    ]
