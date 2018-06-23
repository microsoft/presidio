{{/* vim: set filetype=mustache */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "presidium.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "presidium.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "presidium.analyzer.fullname" -}}
{{ include "presidium.fullname" . | printf "%s-analyzer" }}
{{- end -}}
{{- define "presidium.anonymizer.fullname" -}}
{{ include "presidium.fullname" . | printf "%s-anonymizer" }}
{{- end -}}
{{- define "presidium.api.fullname" -}}
{{ include "presidium.fullname" . | printf "%s-api" }}
{{- end -}}
{{- define "presidium.scheduler.fullname" -}}
{{ include "presidium.fullname" . | printf "%s-scheduler" }}
{{- end -}}

{{- define "presidium.rbac.version" }}rbac.authorization.k8s.io/v1beta1{{ end -}}