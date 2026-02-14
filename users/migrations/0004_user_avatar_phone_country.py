from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_create_manager_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="users/avatars/",
                verbose_name="Аватар",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                verbose_name="Номер телефона",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="country",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Страна",
            ),
        ),
    ]
