# PixTag
PixTag is an AWS-powered serverless picture storage solution with advanced tagging capabilities. The primary objective of this project is to develop and implement an online system that enables users to save and retrieve images with automatically generated and user-generated tags. The software quickly and efficiently handles item detection, tagging, photo uploads, and querying through the use of AWS services such as S3, Lambda, API Gateway, and DynamoDB. It is easy to search for and retrieve information based on these tags since object recognition techniques may be used to automatically identify user-uploaded photographs. The technology also permits human tag updates, ensuring accuracy and adaptability in the picture classification process.

## Components Used
- **Simple Storage Service (Amazon S3):** Used to store the thumbnails that match to the submitted photographs. S3 offers very durable and scalable object storage, which makes it perfect for managing massive amounts of picture data.
- **AWS Lambda:** Lambda functions are used for many different activities, such processing tag-related queries, detecting objects, and producing thumbnails of submitted photos. Lambda enables serverless architecture by enabling code execution without the need for server provisioning or management.
- **DynamoDB on Amazon:** A NoSQL database service that stores picture metadata, such as S3 URLs and recognised tags. DynamoDB provides smooth scaling along with quick and reliable performance.
- **API Gateway:** In order to facilitate user interaction with the system, API Gateway functions as the front-end for the application's API endpoints. This allows users to submit photos, query tags, and manage tags. It offers a safe and scalable API administration layer.
- **Amazon Cognito:** Used to authorise and authenticate users and guarantee that only authorised users are able to access the resources of the application. Access control, sign-in, and user registration are made easier with Cognito.

## System Architecture
- **User Interface:** Users can interact with the programme by managing activities like uploading photos, submitting enquiries, and updating tags using a web-based user interface.
- **AWS Cognito for authentication:** Before using any application features, users using AWS Cognito need to authenticate. Cognito ensures secure system access and manages user login credentials.
- **API Gateway:** Acts as the point of entry for all requests made by users. Depending on the kind of request, it initiates several Lambda tasks, including picture upload, tag searches, and image management.
- **Uploading Images to S3:** An photograph uploaded by a user is kept in an Amazon S3 bucket. A Lambda function is triggered by this operation to produce an image thumbnail.
- **Thumbnail Creation:** A thumbnail for the uploaded image is created by using a Lambda function. The thumbnail is backed up and sent to the S3 bucket.
- **Locating Items:** Another Lambda function looks for items in the provided image by using YOLO. Detected objects (tags) and the S3 URLs for the images and thumbnails are stored in DynamoDB.
- **DynamoDB:** Maintains track of image metadata, including recognised tags and S3 URLs, to enable efficient image management and querying.
- **Query Handling:** Many Lambda functions handle user requests such as finding photographs by tags, editing tags, deleting images, and retrieving images by thumbnail URL. These procedures interact with DynamoDB to get and update data as needed.

## Architecture diagram
![PixTag_Assignment3 drawio](https://github.com/avinashharesh/PixTag/assets/61133789/12f48187-c1c6-4a4d-a360-8dcdaefc4d28)

## User Guide
- **Signup Page:** To create a new account, enter your email address and the password. The password must have at least,
  - 8-character minimum length
  - Contains at least 1 number
  - Contains at least 1 lowercase letter
  - Contains at least 1 uppercase letter
  - Contains at least 1 special character.
- **Login Page:** Using the account credentials you used to create your account, login to the web page.
- **Upload Image:** When there is a prompt to upload an image, upload any image.
- **Queries:**
  - *Find Images based on the tags:* The Query for find images based on the tags will search the database for the images that has a particular object that you are looking for. For example, if you do the query for the images that have an orange in it, the Query will present the image URL of all the images that have an orange in it. You can cross verify by copying and pasting the given URL in the web browser.
  - *Find images based on the thumbnail’s url:* The Query for Find image by Thumbnail URL will work by providing the image URL which is uploaded in the image upload S3 Bucket. By clicking on the find image, the Query will produce the Thumbnail URL of that particular image.
  - *Find images based on the tags of an image:* Suppose a client uploads an image and processes it, all the objects in the uploaded image will be detected. In the image upload S3 Bucket, all the images with the respective uploaded images with the corresponding tags are found and it provides the Thumbnail URL is given. The URL can be verified in the web browser.
  - *Manual addition or removal of tags with bulk tagging:* Suppose an existing image in the S3 Bucket has to be modified based on the tags and counts, the URL of the image should be uploaded, followed by the tags that we wish to be added and the total number of the tag. Upon clicking on Adding/Removing Tags, the new modified tags and the respective counts will be added to the image and can be verified in the Dynamo DB.
  - *Delete images:* Suppose if there is an image that should be deleted from the image upload S3 Bucket, the image URL can be provided and upon clicking on “Delete image”, the corresponding image will be permanently deleted from the Image Upload S3 Bucket.
- **Logout:** Whenever you want to logout of the web application, you can always press logout at the top left part of the page.

## Conclusion
AWS services' power and flexibility are demonstrated by the PixTag project, which created a serverless, scalable, and efficient picture storage system with advanced tagging. Together, our team created a solid solution that made sharing, tagging, and searching images simple. By combining AWS Lambda, S3, API Gateway, DynamoDB, and Cognito, we were able to create a very safe and useful application. Through the process of overcoming obstacles and utilising individual skills, our team established a system that satisfies assignment criteria and provides a strong basis for further enhancements. This project has been a priceless educational opportunity that has equipped us for developing cloud-based applications in the real world.


