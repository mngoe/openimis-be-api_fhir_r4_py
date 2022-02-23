import copy

from insuree.models import Family, Insuree
from insuree.gql_mutations import update_or_create_family
from api_fhir_r4.converters import GroupConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class GroupSerializer(BaseFHIRSerializer):
    fhirConverter = GroupConverter()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        insuree_id = validated_data.get('head_insuree_id')
        if Family.objects.filter(head_insuree_id=insuree_id).count() > 0:
            raise FHIRException('Exists family with the provided head')
        insuree = Insuree.objects.get(id=insuree_id)
        copied_data = copy.deepcopy(validated_data)
        copied_data["head_insuree"] = insuree.__dict__
        copied_data["contribution"] = None
        del copied_data['_state']
        new_family = update_or_create_family(copied_data, user)
        return new_family

    def update(self, instance, validated_data):
        # TODO: This doesn't work
        request = self.context.get("request")
        user = request.user
        chf_id = validated_data.get('chf_id')
        if Family.objects.filter(head_insuree_id=chf_id).count() == 0:
            raise FHIRException('No family with following chfid `{}`'.format(chf_id))
        family = Family.objects.get(head_insuree_id=chf_id, validity_to__isnull=True)
        validated_data["id"] = family.id
        validated_data["uuid"] = family.uuid
        del validated_data['_state']
        instance = update_or_create_family(validated_data, user)
        return instance
