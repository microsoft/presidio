[33mcommit d82bda90e95790fbd6d19b363696a887331095b9[m
Merge: b201762 585e2f4
Author: Omri Mendels <omri374@users.noreply.github.com>
Date:   Mon Mar 25 14:26:36 2019 +0200

    Merge branch 'development' of https://github.com/Microsoft/presidio into development

[33mcommit b201762e592efaf0aaf63260c38e761878b7c786[m
Author: Omri Mendels <omri374@users.noreply.github.com>
Date:   Mon Mar 25 14:16:18 2019 +0200

    Added versions per analyzer dependency in requirements.txt and setup.py

[33mcommit 585e2f45c4172fefec0d9e250bf0a5c8c0b048f9[m
Author: Elad Iwanir <13205761+eladiw@users.noreply.github.com>
Date:   Mon Mar 25 14:08:39 2019 +0200

    Bug666 - Adding pylint to the Analyzer microservice (#105)
    
    * Adding pylint for the analyzer microservice

[33mcommit 50948022034446aa0a52fa2d7404fe2aa2868772[m
Author: Itye Richter <itye.richter@microsoft.com>
Date:   Tue Mar 5 14:32:45 2019 +0200

    fixed bug: changed 'push' to 'pull' in Makefile (#102)

[33mcommit 61c65a2693250f18fe7a4c1cce22092dc71fac69[m
Author: Limor Lahiani <limorl@microsoft.com>
Date:   Mon Feb 25 19:17:42 2019 +0200

    Fix Bug #604 - Refactor test assertions + some pylint fixes (#100)
    
    * Fix Bug #604 - Refactor test assertions + some pylint fixes
    
    * fix spaces in spacy_recognizer.py
    
    * Update test_spacy_recognizer.py
    
    Fix PR comment regarding Bug 617

[33mcommit 5ed4a1375d685778e52e5dce2b5900e1cf5076cb[m
Author: Itye Richter <itye.richter@microsoft.com>
Date:   Sun Feb 17 23:06:31 2019 +0200

    Presidio support for language code in template (#98)
    
    Configure a language code on the request level and not the field level. All requests should have one language

[33mcommit 1df7fdefe78bf711560c319121366b7064cdc601[m
Author: Ilana Kantorov <ilanak@microsoft.com>
Date:   Tue Feb 12 15:23:24 2019 +0200

    Analyzer redesign + supporting custom recognizers
    
    This commit is the first part of the redesign of the analyzer service, and contains the following:
    
        1. Separates spacy and recognizers logic to different files.
    
        2. Implements a base class for all the recognizers,(which in future custom recognizers will inherit)
    
        3. Moves the analyzer logic from main to analyzer_engine class
    
        4. Removes the detected text from the analyzer result.
    
    
    Future commits will contain the following:
    
        1. Dynamic loading of the pre-defined recognizers. [link](https://dev.azure.com/csedevil/Presidio-internal/_sprints/taskboard/Presidio%20Crew/Presidio-internal/02%20-%20Testable%20custom%20models)
    
        2. Add new pattern recognizer via api call, [work item](https://dev.azure.com/csedevil/Presidio-internal/_sprints/taskboard/Presidio%20Crew/Presidio-internal/02%20-%20Testable%20custom%20models)
    
        3. Improve remove duplicates logic [bug](https://dev.azure.com/csedevil/Presidio-internal/_workitems/edit/597) and [bug](https://dev.azure.com/csedevil/Presidio-internal/_workitems/edit/596/)
    
        4. Re-support context model. [work item](https://dev.azure.com/csedevil/Presidio-internal/_sprints/taskboard/Presidio%20Crew/Presidio-internal/02%20-%20Testable%20custom%20models)
    
    
    Current Design:
    ![image](https://user-images.githubusercontent.com/13463870/52433948-edc69480-2b16-11e9-98d7-8923fdc9fb8a.png)

[33mcommit be170c725ca1867258a929550ff4151fd5e56694[m
Author: Itye Richter <itye.richter@microsoft.com>
Date:   Thu Feb 7 10:47:22 2019 +0200

    Deployment script (#95)
    
    New simplified deployment scripts + unified tags

[33mcommit 1e93ad7cf4f4279690d83efaaade6a616cb92624[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Thu Jan 31 10:05:04 2019 +0200

    Streams bug fixes (#92)

[33mcommit 9d831b4613dda180592c5902cca9aded6f2a7d4d[m
Author: Elad Iwanir <13205761+eladiw@users.noreply.github.com>
Date:   Thu Jan 31 09:20:30 2019 +0200

    Default transformation (#94)
    
    * This commit introduce the support of default transformation for undeclared fields in the anonymizer, which can be overrided by the user if supplied another default within the anonymizer template.

[33mcommit 429ea5246e94cb96eaf5df3cbd1f75a77a507b47[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Thu Jan 10 21:30:07 2019 +0200

    Design Diagram change (#90)

[33mcommit fe527b6aa0d7f02c1dc451a55d237be765729636[m
Merge: 0e47661 0eaedbb
Author: torosent <17064840+torosent@users.noreply.github.com>
Date:   Tue Jan 8 17:49:29 2019 +0200

    Merge branch 'development' of https://github.com/Microsoft/presidio into development

[33mcommit 0e476618ee02e4718e972748fcfd252b62509da9[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Tue Jan 8 13:30:13 2019 +0200

    Image support (#87)

[33mcommit 8b0bb20e1c6878fb81654b0c2665e1852866fb25[m
Author: Ilana Kantorov <ilanak@microsoft.com>
Date:   Thu Jan 3 10:40:40 2019 +0200

    Fix abort error to return the error message in the response body (#86)

[33mcommit 74f50249d7f52c75badb19a83f885d74d78bb06e[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Thu Dec 27 10:38:35 2018 +0200

    Create redis cache for templates (#85)

[33mcommit 0eaedbbd40982ff33a2d8a1ba924c77f0213b813[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Tue Jan 8 13:30:13 2019 +0200

    Image support (#87)

[33mcommit 0211822efe074db59cefd788b8a98b2766969148[m
Author: Ilana Kantorov <ilanak@microsoft.com>
Date:   Thu Jan 3 10:40:40 2019 +0200

    Fix abort error to return the error message in the response body (#86)

[33mcommit ee4d270b781b28e39bb4940772b039acbff4c3e4[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Thu Dec 27 10:38:35 2018 +0200

    Create redis cache for templates (#85)

[33mcommit 565cfa4bee2a900a37e7d5abdc94bd60f4b0f290[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Mon Dec 24 14:05:27 2018 +0200

    Add flags and docs (#84)

[33mcommit 8b642e20a2954c15122f6a60412d459647d0a741[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Wed Dec 19 21:37:43 2018 +0200

    Version 0.1.1 (#82)
    
    * Docs (#80)
    
    * Fixed Anonymizer duplicates bug (#81)

[33mcommit 18622490ebbb1bd312b78543b0eca4dd4353f295[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Tue Dec 18 11:53:35 2018 +0200

    Create AUTHORS

[33mcommit 3945113f4001ab517000b9dd6ae5003e50be1e3d[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Tue Dec 18 11:27:04 2018 +0200

    Version 0.1.0 (#78)

[33mcommit b4ff9c11b10677ab983f828cebcaa6b12ec79d4c[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Sat Nov 10 08:48:38 2018 +0200

    Spacy tokens (#75)
    
    * Initial presidio version
    
    * Fixed CPU bug
    
    * Removed kinesis
    
    * Added spacy token option
    
    * Added NHS and change scoring
    
    * Update tests
    
    * Added desc
    
    * Update init for UK
    
    * Update readme

[33mcommit b7aaab002d90888220f818cde6b1f1875ec03d27[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Sat Nov 10 08:46:49 2018 +0200

    Remove kinesis support (#74)
    
    * Initial presidio version
    
    * Fixed CPU bug
    
    * Removed kinesis

[33mcommit e22cb992113959e1960dba85a58499a6d061dde5[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Thu Oct 11 00:37:07 2018 +0300

    Fixed CPU bug

[33mcommit ea4c45bd1ef15dda5ab32f95f88837f444a11725[m
Author: torosent <torosent@microsoft.com>
Date:   Sat Jun 23 11:19:19 2018 +0300

    Initial presidio version

[33mcommit 8d7b1d64544d7e6da365506db15926ad47940c28[m
Merge: 6ae51d8 dd9aa82
Author: torosent <torosent@microsoft.com>
Date:   Thu Sep 6 14:58:34 2018 +0300

    Merge branch 'docs'

[33mcommit dd9aa82267891a19be1a093934f58bf4111d869a[m
Merge: cbcc6a9 6ae51d8
Author: torosent <torosent@microsoft.com>
Date:   Thu Sep 6 14:57:38 2018 +0300

    Merge branch 'master' into docs

[33mcommit 6ae51d81dc02d4106112ec55891f2310a8fd8505[m
Author: torosent <torosent@microsoft.com>
Date:   Thu Sep 6 14:55:37 2018 +0300

    Update docs

[33mcommit cbcc6a979ea8396652fa46d25dff8acc68bd5691[m
Author: Ilana Kantorov <ilanak@microsoft.com>
Date:   Fri Aug 17 13:30:43 2018 +0300

    Update cronjob doc (#58)
    
    * update readme
    
    * minor change

[33mcommit de4a3f102db496bc521a390b475093c21cb2626e[m
Author: ilana <ilanak@microsoft.com>
Date:   Tue Aug 14 16:08:05 2018 +0300

    update scheduler_cronjob

[33mcommit 053d6be0aad4473834f9b14e438e942429ecced1[m
Author: Ilana Kantorov <ilanak@microsoft.com>
Date:   Wed Aug 8 10:57:01 2018 +0300

    update readme (#45)

[33mcommit 292aa44aabe61b7d77bbc298aabe83b717e7a2fa[m
Author: Ilana Kantorov <ilanak@microsoft.com>
Date:   Tue Aug 7 12:33:26 2018 +0300

    Add cronjob readme (#41)
    
    * Update issue templates
    
    * add scheduler cronjob readme
    
    * update readme
    
    * update image

[33mcommit 5aa01c0d9cdd98eef51796c943791f85d0c61049[m
Author: torosent <torosent@microsoft.com>
Date:   Sun Aug 5 15:22:06 2018 +0300

    Update docs

[33mcommit 300ebe5e2acd89be058c5eb382fdde6f0f82b44b[m
Author: torosent <torosent@microsoft.com>
Date:   Sun Aug 5 14:42:38 2018 +0300

    Initial docs version

[33mcommit 8e834b01b96dcb0d9e351f3a0bc0857c330424f2[m
Author: Tomer Rosenthal <torosent@microsoft.com>
Date:   Fri May 4 14:08:59 2018 +0300

    Initial commit
