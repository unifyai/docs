Just a few notes while making changes to the docs,

1. In cases of arguments which are passed as queries such as the `models` param in `/endpoints`, the `name` argument in `/dataset` and so on, the params are defined using the `Query` class so the value used in the `example` is the value used in the docs. For e.g. [this](https://github.com/unifyai/orchestra/blob/c293cc7f9a4532afcba2e0d742d04889e099b740/orchestra/web/api/custom_endpoint/views.py#L62) is where the example value for the key argument used in the `/custom_api_key` endpoint is specified

2. In cases of arguments which are passed as the body of the request such as all the arguments passed to `/chat/completions` or the arguments passed as form data such as with the `/dataset` upload endpoints, the example values are defined as the `”example”` key of the `json_schema_extra` parameter passed to the `Field` object. This may either be as part of the schema (as in case of the [/chat/completions](https://github.com/unifyai/orchestra/blob/c293cc7f9a4532afcba2e0d742d04889e099b740/orchestra/web/api/chat_completion/schema.py#L21) endpoint) or defined in the view signature itself (as in case of the [/dataset](https://github.com/unifyai/orchestra/blob/c293cc7f9a4532afcba2e0d742d04889e099b740/orchestra/web/api/dataset/views.py#L192) upload endpoint.

3. In both of the above cases, `description`, `default`, etc. can be modified through the same places as keyword arguments. Ofc for the endpoints where we pass body, description and default would be in the call of the `Field`/`Form` class itself rather than inside the `json_schema_extra`

4. The error details are picked from the `responses` in the view function (e.g. [here](https://github.com/unifyai/orchestra/blob/c293cc7f9a4532afcba2e0d742d04889e099b740/orchestra/web/api/custom_endpoint/views.py#L49) and the description of the endpoint itself is picked from the docstring of the view function (e.g. [here](https://github.com/unifyai/orchestra/blob/c293cc7f9a4532afcba2e0d742d04889e099b740/orchestra/web/api/custom_endpoint/views.py#L67))

5. There’s some exceptions for endpoints like `/endpoints` where you need to either specify the `model` or the `provider` (and others where certain arguments are optional), I have basically hardcoded to either of the 2 in terms of the example itself and ignored the other one, but making changes to that required making changes to the script [here](https://github.com/unifyai/orchestra/blob/main/docs/query.py#L3)

6. If you add an endpoint which accepts a file upload, [this](https://github.com/unifyai/orchestra/blob/main/docs/form.py#L4) dict would need changing to include that argument name there (because those arguments are passed as form-data rather than json-data in the request)

7. The `/chat/completions` endpoint arguments have been grouped into 3 categories as explained [here](https://docs.unify.ai/universal_api/arguments). This grouping is applied to the API reference page using a mapping like [this](https://github.com/unifyai/orchestra/blob/3c45c269b2776608dba10219b6c9f7b1d0fa91de/docs/body.py#L3). In order to add more sections or edit existing sections, you'd basically need to add the argument above which the header should be added along with the link to that section.

8. The headers for the sections under the API reference page are picked from the tags specified [here](https://github.com/unifyai/orchestra/blob/1c9fa75a8431d8d82634dc5365e40a5019a52a36/orchestra/web/api/router.py). The title of the pages themselves are picked from the openapi spec's `summary`.

9. Some of the formatting is fairly sensitive so I’d suggest going through their [docs](https://mintlify.com/docs/page) to understand how stuff is formatted. For e.g. having multi-line strings like [this](https://github.com/unifyai/orchestra/blob/67a1069df79d657d6ba57f3bdbb5a94a4cbc9bdc/orchestra/web/api/dataset_evaluation/schema.py#L15) wouldn’t work but it would need to be written like [this](https://github.com/unifyai/orchestra/blob/02df65571d4816e33749f3f5a1897b1c2a66830a/orchestra/web/api/dataset_evaluation/schema.py#L19) (with the triple back-tick)

10. Also any descriptions of the form `<model>`, `<model>@<provider>`, etc. get treated as html elements in an mdx file so ideally it should be `\<model\>`, `\<model\>\<provider\>`, etc.

11. There's also formatting issues like [this](https://github.com/unifyai/unify/commit/b5a52fabc9e77f12a2952dac35531ed86904d48a) where `{ "type": "json_object" }` without the back-ticks wouldn't work. Also the ` ` between `{` and the `"` is necessary on both sides.

12. Same applies to code blocks like [this](https://github.com/unifyai/orchestra/blob/0b04c01cae317f2eb7e569e84a3a66f96b21f742/orchestra/web/api/dataset_evaluation/views.py#L746-L761) which should also be enclosed with triple quotes like [this](https://github.com/unifyai/orchestra/commit/99d63db6b2839feab2de456066c311f317c0c5c8) to avoid parsing errors.

13. There are a few endpoints on the docs where either the description of the parameters or the description of the responses with different error codes might be missing, adding those to the above mentioned places should get them working.

14. Finally, given that we’re doing the markdown writing ourselves rather than relying on mintlify, this has lead to some brittleness with the doc building code, so I’d highly recommend setting up the docs locally, which would require
    1. cloning the `unify-docs` repo, followed by `npm i -g mintlify` (also prolly installing `npm` and `node` if not done already), then go inside the `unify-docs` folder and do `npm i` followed by `mintlify dev`. This should run the docs on a local server where you can test how your changes
    2. Copy over the `mint.json` from the latest version of `unify-docs` inside the `unify` folder
    3. in order to build the docs, you’d need to go inside the orchestra folder and do `python docs/main.py` which should build the mdx files, you’d then need to move the `api-reference` folder and replace the `unify-docs/api-reference` folder with that one instead, and also replace the updated `mint.json` in the `unify-doc`s folder. This should give you a preview of how your changes impacted the docs

    OR

    1. Go through the README.md and set things up with `docker`

15. As far as the python client docs go, you would need to
    1. Clone the `unify` repo
    2. Install `pydoc-markdown`
    3. Create a folder named `output`
    4. run the command `pydoc-markdown | tee output/result.txt`
    5. Then you should move the `generate_docs.py` script inside the `output` folder
    6. Run `python output/generate_docs.py`
    7. Once the script is complete, you can copy the `.mdx` files inside the `output` folder inside the `python` folder of the `unify-docs` repo.

16. In case there's a submodule in the python client that docs shouldn't be built for, that submodule should be added to [this](https://github.com/unifyai/unify/blob/28384abae3863ee54ea16672f83a02be1a3673aa/generate_docs.py#L13) list.
