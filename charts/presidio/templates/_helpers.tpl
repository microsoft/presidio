{{/* vim: set filetype=mustache */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "presidio.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "presidio.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "presidio.analyzer.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-analyzer" }}
{{- end -}}
{{- define "presidio.anonymizer.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-anonymizer" }}
{{- end -}}
{{- define "presidio.anonymizerimage.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-anonymizer-image" }}
{{- end -}}
{{- define "presidio.ocr.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-ocr" }}
{{- end -}}
{{- define "presidio.api.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-api" }}
{{- end -}}
{{- define "presidio.scheduler.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-scheduler" }}
{{- end -}}
{{- define "presidio.recognizersstore.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-recognizersstore" }}
{{- end -}}
{{- define "presidio.tester.fullname" -}}
{{ include "presidio.fullname" . | printf "%s-tester" }}
{{- end -}}

{{- define "presidio.analyzer.address" -}}
{{template "presidio.analyzer.fullname" .}}:{{.Values.analyzer.service.externalPort}}
{{- end -}}

{{- define "presidio.recognizersstore.address" -}}
{{template "presidio.recognizersstore.fullname" .}}:{{.Values.recognizersstore.service.externalPort}}
{{- end -}}

{{- define "presidio.anonymizer.address" -}}
{{template "presidio.anonymizer.fullname" .}}:{{.Values.anonymizer.service.externalPort}}
{{- end -}}

{{- define "presidio.anonymizerimage.address" -}}
{{template "presidio.anonymizerimage.fullname" .}}:{{.Values.anonymizerimage.service.externalPort}}
{{- end -}}

{{- define "presidio.ocr.address" -}}
{{template "presidio.ocr.fullname" .}}:{{.Values.ocr.service.externalPort}}
{{- end -}}

{{- define "presidio.scheduler.address" -}}
{{template "presidio.scheduler.fullname" .}}:{{.Values.scheduler.service.externalPort}}
{{- end -}}

{{- define "presidio.rbac.version" }}rbac.authorization.k8s.io/v1beta1{{ end -}}