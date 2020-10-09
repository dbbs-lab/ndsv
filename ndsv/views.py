from django.shortcuts import render
from oauth2_provider.views.generic import ProtectedResourceView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import ndsv.models, ndsv.artifacts, json

def zork(request):
    html = """<html>
        <style>
            body {
                padding: 8px;
                margin: 0;
                overflow: hidden;
                background-color: black;
                height: 100vh;
                color: white;
                font: 1.3rem Inconsolata, monospace;
                text-shadow: 0 0 5px #C8C8C8;
            }
            input[type=text] {
                background-color:rgba(0, 0, 0, 0);
                color:white;
                font: 1.3rem Inconsolata, monospace;
                text-shadow: 0 0 5px #C8C8C8;
                border: none;
                outline:none;
                height:30px;
                caret-color: white;
            }
        </style>
        <body style="">
            <script>
                function my_func(el) {
                    console.log("ola");
                }
            </script>
            <p>
                You're standing in front of a large vault with countless ancient artifacts inside.
            </p>
            $&gt; <input id="in" type="text" onblur="this.focus()" onkeydown="event.key == 'Enter' ? this.value = '' : ''"></input>
            <script>
                document.getElementById("in").focus()
            </script>
        </body>
    </html>"""
    return HttpResponse(html)

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
        return artifact.as_response(file)
