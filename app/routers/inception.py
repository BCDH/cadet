from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from app.util.login import get_current_username
from typing import Any, Dict
from collections import namedtuple
import spacy
from cassis import Cas
from cassis import TypeSystem, load_typesystem, load_cas_from_xmi

nlp = spacy.load("en_core_web_sm", disable=["parser"])

# Types

JsonDict = Dict[str, Any]

PredictionRequest = namedtuple(
    "PredictionRequest", ["layer", "feature", "projectId", "document", "typeSystem"]
)
PredictionResponse = namedtuple("PredictionResponse", ["document"])
Document = namedtuple("Document", ["xmi", "documentId", "userId"])

# Constants

SENTENCE_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
TOKEN_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"
IS_PREDICTION = "inception_internal_predicted"


# Util functions
def parse_prediction_request(json_object: JsonDict) -> PredictionRequest:
    metadata = json_object["metadata"]
    document = json_object["document"]

    layer = metadata["layer"]
    feature = metadata["feature"]
    projectId = metadata["projectId"]

    xmi = document["xmi"]
    documentId = document["documentId"]
    userId = document["userId"]
    typesystem = json_object["typeSystem"]

    return PredictionRequest(
        layer, feature, projectId, Document(xmi, documentId, userId), typesystem
    )


# Router
router = APIRouter(dependencies=[Depends(get_current_username)])

# INCEpTION posts a request to the endpoint
# the request includes cas/xml serialized as xmi (this is the text and existing annotation data)
# the app adds annotations to the cas
# the app returns the Document

# https://github.com/inception-project/inception-external-recommender/blob/master/ariadne/server.py
# Chunk, Lemma, Morphological Features, Named Entity, Orthography Correction, Part of Speech,


@router.get("/pos/predict")
async def pos1_predict(request: Request):
    return {"hi there": "I'm pos"}


# POS 👩‍🚀🧑‍🚀👨‍🚀
@router.post("/pos/predict")
def pos_predict(request: Request):
    json_data = request.json()
    prediction_request = parse_prediction_request(json_data)
    prediction_response = predict_pos(prediction_request)
    return prediction_response.document


# @router.post("/pos/train")
# async def pos_train(cas: Cas, layer: str, feature: str, project_id: str, document_id: str, user_id: str):
#     pass check that <class 'cassis.cas.Cas'> is a valid pydantic field type


def predict_pos(prediction_request: PredictionRequest) -> PredictionResponse:
    # Load the CAS and type system from the request
    typesystem = load_typesystem(prediction_request.typeSystem)
    cas = load_cas_from_xmi(prediction_request.document.xmi, typesystem=typesystem)
    AnnotationType = typesystem.get_type(prediction_request.layer)

    # Extract the tokens from the CAS and create a spacy doc from it
    tokens = list(cas.select(TOKEN_TYPE))
    words = [cas.get_covered_text(token) for token in tokens]
    doc = Doc(nlp.vocab, words=words)

    # Do the tagging
    nlp.tagger(doc)

    # For every token, extract the POS tag and create an annotation in the CAS
    for token in doc:
        fields = {
            "begin": tokens[token.i].begin,
            "end": tokens[token.i].end,
            IS_PREDICTION: True,
            prediction_request.feature: token.pos_,
        }
        annotation = AnnotationType(**fields)
        cas.add_annotation(annotation)

    xmi = cas.to_xmi()
    return PredictionResponse(xmi)


# 👩‍🚀 LEMMA 👨‍🚀
@router.post("/lemma/predict")
async def lemma_predict(request: Request):
    json_data = request.json()
    prediction_request = parse_prediction_request(json_data)
    prediction_response = predict_lemma(prediction_request)
    return prediction_response.document


def predict_lemma(prediction_request: PredictionRequest) -> PredictionResponse:
    # Load the CAS and type system from the request
    typesystem = load_typesystem(prediction_request.typeSystem)
    cas = load_cas_from_xmi(prediction_request.document.xmi, typesystem=typesystem)
    AnnotationType = typesystem.get_type(prediction_request.layer)

    # Extract the tokens from the CAS and create a spacy doc from it
    tokens = list(cas.select(TOKEN_TYPE))
    words = [cas.get_covered_text(token) for token in tokens]
    doc = Doc(nlp.vocab, words=words)

    # Do the tagging
    nlp.tagger(doc)

    # For every token, extract the LEMMA tag and create an annotation in the CAS
    for token in doc:
        fields = {
            "begin": tokens[token.i].begin,
            "end": tokens[token.i].end,
            IS_PREDICTION: True,
            prediction_request.feature: token.lemma_,
        }
        annotation = AnnotationType(**fields)
        cas.add_annotation(annotation)

    xmi = cas.to_xmi()
    return PredictionResponse(xmi)
