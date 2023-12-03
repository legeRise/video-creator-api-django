from rest_framework import serializers
from .models import Keyword

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'


    def toList(self,topdisp,sep=",",remove_spaces=False):
        topdisp =topdisp.split(sep)
        return [keyword.replace(" ", "") for keyword in topdisp] if remove_spaces else topdisp

    def toString(self,topdisp,sep=','):
        return sep.join(topdisp)
    
    def validate(self,data):
        pic =self.toList(data.get('pic_keywords'),remove_spaces=True)
        display = self.toList(data.get('display_keywords'))

        if len(pic)!=len(display):
            raise serializers.ValidationError("Both Fields Should Have Same Number of Items")
        if not 3 <= len(pic) <= 10:
            raise serializers.ValidationError(f"The number of items should be between 3 and 10, but you provided {len(pic)} items.")
        
        data['pic_keywords'] = self.toString(pic) # converting space-removed version of list to string to store database
        return data

