from django.conf import settings
import pathlib, io, uuid, tarfile, os, shutil
from django.db.utils import IntegrityError
from .models import EtchingPlate
import copy, json

class PayloadError(Exception):
    pass

class RaceError(Exception):
    pass

class RestrictAccess:
    def make_private(self):
        pass

    def grant_access(self):
        pass

    def has_access(self, user):
        pass


class Beam:
    def __init__(self, id, root=None, incoming=False):
        if root is None:
            root = get_static_root()
        self.root = pathlib.Path(root)
        self.incoming = incoming
        if incoming:
            self.tmp_id = id
        else:
            self.etched(id)

    def etched(self, id):
        self.id = id
        self.path = self.root / id
        self.read_config()

    def get_artifact(self, id):
        return Artifact(self, id)

    def get_artifacts(self):
        return [Artifact(self, int(id)) for id in os.listdir(self.path) if id.isdigit()]

    def read_config(self):
        pass

    def etch(self, user, archive, meta):
        self.tmp_path = tmp = pathlib.Path("/tmp/ndsv-" + self.tmp_id)
        with tarfile.open(fileobj=archive.open(mode="rb"), mode="r") as arc:
            if not arc.next().isdir():
                raise PayloadError("The toplevel tarfile should be a directory.")
            arc.extractall(str(tmp))
        payload_root = self.validate_payload()
        return self.etch_payload(user, payload_root, meta)

    def validate_payload(self):
        toplevel = os.listdir(self.tmp_path)
        if len(toplevel) != 1 or not (self.tmp_path / toplevel[0]).is_dir():
            raise PayloadError("There may only be 1 toplevel object and it must be a directory.")
        payload_root = self.tmp_path / toplevel[0]
        return payload_root

    def etch_payload(self, user, payload, meta):
        id = self.tmp_id
        reserved = {'id', 'beam'}
        fields = set(field.name for field in EtchingPlate._meta.get_fields())
        valid = fields - {'beam_id', 'id'}
        supplied = set(meta.keys())
        invalid = supplied - valid
        if invalid:
            raise PayloadError(f"Invalid meta keys {invalid} supplied. Valid meta keys: {valid}")
        while True:
            try:
                etch = EtchingPlate.objects.create(etched_by=user, beam_id=id, **meta)
                break
            except IntegrityError:
                id = str(uuid.uuid4())
        self.etched(id)
        shutil.move(payload, self.path)
        # Make sure the uploading user has access to its own artifacts
        for artifact in self.get_artifacts():
            access = artifact.json.get("access_list", [])
            if user.username not in access:
                print(f"Adding uploading user '{user.username}' to access list")
                access.append(user.username)
                artifact.json({"access_list": access})
        return etch

    @classmethod
    def receive(cls, user, archive, meta):
        tmp_id = str(uuid.uuid4())
        beam = cls(tmp_id, incoming=True)
        beam.etch(user, archive, meta)
        return beam


class ArtifactJson(dict):
    def __init__(self, path, initial):
        self.path = path
        self.update(copy.deepcopy(initial))

    def __call__(self, update):
        self.update(copy.deepcopy(update))
        with open(self.path, "w") as f:
            json.dump(self, f)


class Artifact:
    def __init__(self, beam, id):
        self.id = id
        self.beam = beam
        self.root = beam.path
        self.path = beam.path / str(id)
        self.read_json()

    def read_json(self):
        json_path = self.path / "artifact.json"
        with open(json_path, "r") as f:
            self.json = ArtifactJson(json_path, json.load(f))

    def has_access(self, user):
        print(self.json)
        return self.json["public_access"] or user.username in self.json["access_list"]

    def as_response(self, file):
        from django.http import FileResponse
        return FileResponse(open(self.path / file, 'rb'))



def get_static_root():
    path = pathlib.Path(settings.NDSV_STORAGE_VAULT)
    if not path.exists():
        raise RuntimeError(f"Static NDSV file root '{path}' does not exist.")
    return path
