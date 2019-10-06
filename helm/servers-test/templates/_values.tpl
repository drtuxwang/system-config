{{- define "chart.name" -}}
{{-   .Chart.Name -}}
{{- end -}}

{{- define "chart.appname" -}}
{{- .Release.Name | trunc 53 | trimSuffix "-" -}}
{{- end -}}

{{- define "chart.image.name" -}}
{{-   .Values.image.name -}}
{{- end -}}
