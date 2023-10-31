# OPUS-MT Translation Service

OPUS-MT Translation Service is a machine translation service that can run on most computers. The service is mostly intended for internal use at organizations, where it can be made available through the organization's internal network using Kubernetes or OpenShift container platform. However, the service can also be used on just one computer, or hosted on the Internet for anyone to use.

The service can be used to run [OPUS-MT machine translation models](https://opus.nlpl.eu/dashboard/index.php?model=all&test=all&pkg=opusmt), which are available for hundreds of language pairs. The OPUS-MT models can be further fine-tuned with domain-specific data (e.g. organizations translation memories) by using [OPUS-CAT](https://helsinki-nlp.github.io/OPUS-CAT/finetune).

## Setting up the service on a container platform

1. Clone this repository.
2. Use [OPUS-CAT](https://helsinki-nlp.github.io/OPUS-CAT/install) to download the models that you want to be made available via the web service.
3. (Optional) [Fine-tune](https://helsinki-nlp.github.io/OPUS-CAT/finetune) the models with your own data in OPUS-CAT.
4. For each OPUS-CAT model that you want to be included in the translation service, click **Edit model tags** and add the tag _ct2_ to the model tags.
5. Convert the models into Ctranslate2 models by running the _opus_mt_conversion/opuscat-ct2.py_ script (note: only one model per language pair will be converted, even if multiple models have been tagged with _ct2_). The script requires that the _pycountry_ and _ctranslate2_ modules have been installed with pip.
6. Zip the converted models to a file _models.zip_ and add the file to the repository root (Git LFS is recommended, as the file can be large).
7. If you are using the OpenShift container platform, you can deploy the app by using the [Import from Git functionality in OpenShift](https://access.redhat.com/documentation/en-us/red_hat_openshift_data_science/1/html/developing_a_data_model/creating-an-openshift-application-from-a-git-repository_deploy-models). Deployment on Kubernetes has not been tested, but as the platforms are compatible, the service should be deployable on Kubernetes using a similar functionality.

## Credits

This work is built on open source software developed by others. The web service is a slightly modified version of [LibreTranslate](https://libretranslate.com), which itself utilizes the [Argos Translate](https://github.com/argosopentech/argos-translate) translation library (which uses the [CTranslate2](https://github.com/OpenNMT/CTranslate2) library for generating translations). This service is not officially associated with LibreTranslate or its products.

## License

[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html)
