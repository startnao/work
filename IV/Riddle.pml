<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Riddle" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs>
        <Dialog name="ExampleDialog" src="behavior_1/ExampleDialog/ExampleDialog.dlg" />
    </Dialogs>
    <Resources>
        <File name="choice_sentences" src="behavior_1/Aldebaran/choice_sentences.xml" />
        <File name="bnxv" src="bnxv" />
        <File name="activate_choregraphe" src="activate_choregraphe.txt" />
        <File name="choice_sentences_light" src="behavior_1/Aldebaran/choice_sentences_light.xml" />
    </Resources>
    <Topics>
        <Topic name="ExampleDialog_enu" src="behavior_1/ExampleDialog/ExampleDialog_enu.top" topicName="ExampleDialog" language="enu" />
        <Topic name="ExampleDialog_frf" src="behavior_1/ExampleDialog/ExampleDialog_frf.top" topicName="ExampleDialog" language="frf" />
    </Topics>
    <IgnoredPaths />
</Package>
