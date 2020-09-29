from django.conf import settings
import pathlib, io, uuid, tarfile, os, shutil
from django.db.utils import IntegrityError
from .models import EtchingPlate

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
    def __init__(self, id, root, incoming=False):
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
        return []

    def read_config(self):
        pass

    def etch(self, archive, meta):
        self.tmp_path = tmp = pathlib.Path("/tmp/ndsv-" + self.tmp_id)
        with tarfile.open(fileobj=archive.open(mode="rb"), mode="r") as arc:
            if not arc.next().isdir():
                raise PayloadError("The toplevel tarfile should be a directory.")
            arc.extractall(str(tmp))
        payload_root = self.validate_payload()
        return self.etch_payload(payload_root, meta)

    def validate_payload(self):
        toplevel = os.listdir(self.tmp_path)
        if len(toplevel) != 1 or not (self.tmp_path / toplevel[0]).is_dir():
            raise PayloadError("There may only be 1 toplevel object and it must be a directory.")
        payload_root = self.tmp_path / toplevel[0]
        return payload_root

    def etch_payload(self, payload, meta):
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
                etch = EtchingPlate.objects.create(beam_id=id, **meta)
                break
            except IntegrityError:
                id = str(uuid.uuid4())
        self.etched(id)
        shutil.move(payload, self.path)
        return etch

    @classmethod
    def receive(cls, archive, meta):
        storage = get_static_root()
        tmp_id = str(uuid.uuid4())
        beam = cls(tmp_id, storage, incoming=True)
        beam.etch(archive, meta)
        return beam

class Artifact:
    def __init__(self, beam, id):
        self.id = id
        self.beam = beam
        self.root = beam.path
        self.path = beam.path / str(id)
        self.read_config()

    def read_config(self):
        with open(self.path / "artifact.json", "r") as f:
            self.config = json.load(f)

    def has_access(self, user):
        return self.config["public_access"] or user.name in self.config["access_list"]

def get_static_root():
    path = pathlib.Path(settings.NDSV_STORAGE_VAULT)
    if not path.exists():
        raise RuntimeError(f"Static NDSV file root '{path}' does not exist.")
    return path
