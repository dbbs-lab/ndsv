from django.shortcuts import render
from oauth2_provider.views.generic import ProtectedResourceView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import ndsv.models, ndsv.artifacts, json
import os

def zork(request):
    with open(os.path.join(os.path.dirname(__file__), "vault.html"), "r") as f:
        return HttpResponse(f.read())

class RedshiftQuasarGalaxyBeamRecepticle(ProtectedResourceView):
    """
        Beam upload endpoint
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "archive" not in request.FILES:
            return HttpResponseBadRequest()
        try:
            meta = json.loads(request.POST['meta'])
        except:
            return HttpResponseBadRequest()
        meta["access_list"] = meta.get("access_list", [])
        if request.user.username not in meta["access_list"]:
            meta["access_list"].append(request.user.username)
        beam = ndsv.artifacts.Beam.receive(request.user, request.FILES["archive"], meta)
        return HttpResponse(json.dumps({"id": beam.id}))

class BeltramiPseudosphereEmitter(View):
    """
        Artifact download endpoint
    """
    def get(self, request, beam_id, artifact_id, file, *args, **kwargs):
        plate = ndsv.models.get_etching_plate(beam_id)
        if not plate or not plate.has_access(request.user):
            print(f"Plate access denied read permission to beam")
            raise PermissionDenied()
        beam = plate.get_beam()
        artifact = beam.get_artifact(artifact_id)
        if not artifact.has_access(request.user):
            print("User:", request.user, request.user.is_authenticated)
            print(f"Denying artifact read permission for artifact {artifact.id} of beam {artifact.beam.id}")
            raise PermissionDenied()
        try:
            return artifact.as_response(file)
        except IOError:
            raise Http404("Artifact file does not exist") from None
