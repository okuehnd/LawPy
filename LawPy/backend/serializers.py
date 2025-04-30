

# from rest_framework import serializers
# from .models import Case

# class CaseSerializer(serializers.Serializer):
#     id = serializers.CharField(read_only=True)
#     title = serializers.CharField()
#     court = serializers.CharField()
#     full_text = serializers.CharField()
#     date_filed = serializers.DateTimeField()

#     def create(self, validated_data):
#         return Case.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         instance.title = validated_data.get('title', instance.title)
#         instance.court = validated_data.get('court', instance.court)
#         instance.full_text = validated_data.get('full_text', instance.full_text)
#         instance.date_filed = validated_data.get('date_filed', instance.date_filed)
#         instance.save()
#         return instance