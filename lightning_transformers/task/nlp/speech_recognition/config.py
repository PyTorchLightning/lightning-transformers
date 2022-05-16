# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import dataclass

from lightning_transformers.core.nlp import HFTransformerDataConfig


@dataclass
class SpeechRecognitionConfig(HFTransformerDataConfig):
    do_normalize: bool = True
    return_attention_mask: bool = False


@dataclass
class SpeechRecognitionDataConfig(HFTransformerDataConfig):
    max_length = 5
    sampling_rate: int = 16000
    padding: float = 0.0
    
